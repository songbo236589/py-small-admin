"""
Content 话题服务 - 负责话题抓取和管理的业务逻辑
"""

import json
from typing import Any

from loguru import logger

from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy.orm import load_only, selectinload
from sqlmodel import select

from Modules.common.libs.database.sql.session import get_async_session
from Modules.common.libs.responses.response import error, success
from Modules.common.libs.time.utils import format_datetime, now
from Modules.common.libs.validation.pagination_validator import CustomParams
from Modules.common.services.base_service import BaseService
from Modules.content.models.content_category import ContentCategory
from Modules.content.models.content_platform_account import ContentPlatformAccount
from Modules.content.models.content_topic import ContentTopic
from Modules.content.services.publisher import ZhihuHandler


class TopicService(BaseService):
    """Content话题服务 - 负责话题抓取和管理的业务逻辑"""

    def __init__(self):
        super().__init__()

    async def _match_category(self, category_name: str | None) -> int | None:
        """
        根据分类名称匹配分类ID

        Args:
            category_name: 平台抓取的分类名称

        Returns:
            匹配的分类ID，如果未找到则返回 None
        """
        if not category_name:
            return None

        async with get_async_session() as session:
            # 1. 尝试精确匹配分类名称
            result = await session.execute(
                select(ContentCategory).where(
                    ContentCategory.name == category_name,
                    ContentCategory.status == 1,  # 只匹配启用的分类
                )
            )
            category = result.scalar_one_or_none()
            if category:
                return category.id

            # 2. 尝试模糊匹配（忽略大小写）
            result = await session.execute(
                select(ContentCategory).where(
                    ContentCategory.name.icontains(category_name),
                    ContentCategory.status == 1,
                )
            )
            category = result.scalar_one_or_none()
            if category:
                return category.id

        # 未找到匹配的分类
        return None

    async def fetch_topics(
        self, platform: str, platform_account_id: int, limit: int = 20
    ) -> JSONResponse:
        """从指定平台获取推荐话题（同步执行）

        Args:
            platform: 平台标识（zhihu）
            platform_account_id: 平台账号ID
            limit: 获取数量

        Returns:
            JSONResponse: 抓取结果
        """
        # 1. 验证平台账号
        async with get_async_session() as session:
            account_result = await session.execute(
                select(ContentPlatformAccount).where(
                    ContentPlatformAccount.id == platform_account_id,
                    ContentPlatformAccount.platform == platform,
                    ContentPlatformAccount.status == 1,  # 1=有效
                )
            )
            account = account_result.scalar_one_or_none()

            if not account:
                return error("平台账号不存在或已失效")

            # 2. 解析 Cookies
            try:
                cookies = json.loads(account.cookies) if account.cookies else []
            except json.JSONDecodeError:
                return error("Cookie 格式错误，无法解析")

            # 3. 获取对应的处理器
            handlers = {
                "zhihu": ZhihuHandler,
            }

            handler_class = handlers.get(platform)
            if not handler_class:
                return error(f"不支持的平台: {platform}")

            # 4. 执行抓取（同步等待完成）
            try:
                handler = handler_class(cookies=cookies, user_agent=account.user_agent)
                questions = await handler.fetch_recommended_questions(limit=limit)

                # 5. 存储到数据库（去重）
                created_count = 0
                updated_count = 0
                skipped_count = 0

                for q in questions:
                    # 检查是否已存在
                    existing = await session.execute(
                        select(ContentTopic).where(
                            ContentTopic.platform == platform,
                            ContentTopic.platform_question_id == q["question_id"],
                        )
                    )
                    existing_topic = existing.scalar_one_or_none()

                    # 匹配分类ID
                    category_name = q.get("category")
                    category_id = await self._match_category(category_name)

                    topic_data = {
                        "platform": platform,
                        "platform_question_id": q["question_id"],
                        "title": q["title"],
                        "description": q.get("description"),
                        "url": q.get("url"),
                        "view_count": q.get("view_count", 0),
                        "answer_count": q.get("answer_count", 0),
                        "follower_count": q.get("follower_count", 0),
                        "category_id": category_id,  # 使用 category_id 替代 category
                        "hot_score": q.get("hot_score"),
                        "author_name": q.get("author_name"),
                        "author_url": None,
                        "fetched_at": now(),
                    }

                    if existing_topic:
                        # 更新已存在的话题
                        for key, value in topic_data.items():
                            setattr(existing_topic, key, value)
                        updated_count += 1
                    else:
                        # 创建新话题
                        new_topic = ContentTopic(**topic_data)
                        new_topic.created_at = now()
                        session.add(new_topic)
                        created_count += 1

                await session.commit()

                return success(
                    {
                        "total": len(questions),
                        "created": created_count,
                        "updated": updated_count,
                        "skipped": skipped_count,
                        "platform": platform,
                        "message": f"成功抓取 {len(questions)} 个话题（新增 {created_count} 个，更新 {updated_count} 个）",
                    }
                )

            except Exception as e:
                return error(f"抓取失败: {str(e)}")

    async def index(self, data: dict[str, Any]) -> JSONResponse:
        """获取话题列表或搜索话题（统一接口）"""
        page = data.get("page", 1)
        size = data.get("limit", 20)

        # 模糊匹配字段字典
        data["fuzzy_fields"] = ["title", "author_name"]
        # 精确匹配字段字典
        data["exact_fields"] = ["platform", "status"]
        # 应用范围筛选
        data["range_fields"] = ["hot_score", "view_count", "answer_count", "fetched_at"]

        # 特殊处理 category_id 筛选（支持 __NONE__ 查询未分类话题）
        category_id_value = data.get("category_id")
        has_category_filter = False

        async with get_async_session() as session:
            # 构建基础查询，使用关系映射加载 ContentCategory
            query = select(ContentTopic).options(
                load_only(
                    *[
                        ContentTopic.id,
                        ContentTopic.platform,
                        ContentTopic.platform_question_id,
                        ContentTopic.title,
                        ContentTopic.description,
                        ContentTopic.url,
                        ContentTopic.view_count,
                        ContentTopic.answer_count,
                        ContentTopic.follower_count,
                        ContentTopic.category_id,
                        ContentTopic.hot_score,
                        ContentTopic.author_name,
                        ContentTopic.author_url,
                        ContentTopic.status,
                        ContentTopic.fetched_at,
                        ContentTopic.article_count,
                        ContentTopic.created_at,
                    ]
                ),
                selectinload(ContentTopic.category).load_only(
                    *[ContentCategory.id, ContentCategory.name, ContentCategory.slug]
                ),
            )

            # 搜索
            query = await self.apply_search_filters(query, ContentTopic, data)

            # 特殊处理 category_id 筛选（支持 __NONE__ 查询未分类话题）
            if category_id_value == "__NONE__":
                query = query.where(ContentTopic.category_id == None)
            elif category_id_value is not None:
                query = query.where(ContentTopic.category_id == int(category_id_value))

            # 特殊处理 has_description 筛选（查询描述是否存在）
            has_description = data.get("has_description")
            if has_description == "has":
                query = query.where(
                    ContentTopic.description.isnot(None),
                    ContentTopic.description != ""
                )
            elif has_description == "none":
                query = query.where(
                    (ContentTopic.description == None) | (ContentTopic.description == "")
                )

            # 应用排序（默认按热度降序）
            if not data.get("sort"):
                query = query.order_by(ContentTopic.hot_score.desc())  # type: ignore
            else:
                query = await self.apply_sorting(query, ContentTopic, data.get("sort"))

            page_data = await paginate(
                session, query, CustomParams(page=page, size=size)
            )
            items = []
            for topic in page_data.items:
                d = topic.__dict__.copy()
                d["fetched_at"] = (
                    format_datetime(topic.fetched_at) if topic.fetched_at else None
                )
                d["created_at"] = (
                    format_datetime(topic.created_at) if topic.created_at else None
                )
                # 处理分类信息
                if topic.category:
                    d["category_name"] = topic.category.name
                    d["category_slug"] = topic.category.slug
                    d.pop("category", None)  # 移除关联对象
                items.append(d)

            return success(
                jsonable_encoder(
                    {
                        "items": items,
                        "total": page_data.total,
                        "page": page_data.page,
                        "size": page_data.size,
                        "pages": page_data.pages,
                    }
                )
            )

    async def detail(self, id: int) -> JSONResponse:
        """获取话题详情"""
        async with get_async_session() as session:
            result = await session.execute(
                select(ContentTopic).where(ContentTopic.id == id)
            )
            topic = result.scalar_one_or_none()

            if not topic:
                return error("话题不存在")

            # 获取分类信息
            category_info = None
            if topic.category_id:
                category_result = await session.execute(
                    select(ContentCategory).where(ContentCategory.id == topic.category_id)
                )
                category = category_result.scalar_one_or_none()
                if category:
                    category_info = {
                        "id": category.id,
                        "name": category.name,
                        "slug": category.slug,
                    }

            info = {
                "id": topic.id,
                "platform": topic.platform,
                "platform_question_id": topic.platform_question_id,
                "title": topic.title,
                "description": topic.description,
                "url": topic.url,
                "view_count": topic.view_count,
                "answer_count": topic.answer_count,
                "follower_count": topic.follower_count,
                "category_id": topic.category_id,
                "category": category_info,
                "hot_score": topic.hot_score,
                "author_name": topic.author_name,
                "author_url": topic.author_url,
                "status": topic.status,
                "fetched_at": format_datetime(topic.fetched_at)
                if topic.fetched_at
                else None,
                "zhihu_content": topic.zhihu_content,
                "zhihu_content_updated_at": format_datetime(topic.zhihu_content_updated_at)
                if topic.zhihu_content_updated_at
                else None,
                "created_at": format_datetime(topic.created_at)
                if topic.created_at
                else None,
            }

            return success(info)

    async def set_status(self, id: int, data: dict[str, Any]) -> JSONResponse:
        """话题状态"""
        return await self.common_update(id=id, data=data, model_class=ContentTopic)

    async def destroy(self, id: int) -> JSONResponse:
        """删除话题"""
        return await self.common_destroy(id=id, model_class=ContentTopic)

    async def destroy_all(self, id_array: list[int]) -> JSONResponse:
        """批量删除话题"""
        return await self.common_destroy_all(
            id_array=id_array, model_class=ContentTopic
        )

    async def update_description(
        self, id: int, description: str
    ) -> JSONResponse:
        """更新话题的描述

        Args:
            id: 话题ID
            description: 新的描述内容

        Returns:
            JSONResponse: 更新结果
        """
        async with get_async_session() as session:
            result = await session.execute(
                select(ContentTopic).where(ContentTopic.id == id)
            )
            topic = result.scalar_one_or_none()

            if not topic:
                return error("话题不存在")

            # 更新描述
            topic.description = description
            await session.commit()

            return success(
                {
                    "id": topic.id,
                    "description": topic.description,
                    "message": "描述更新成功",
                }
            )

    async def update_category(
        self, id: int, category_id: int | None
    ) -> JSONResponse:
        """更新话题分类

        Args:
            id: 话题ID
            category_id: 分类ID（None 表示清空分类）

        Returns:
            JSONResponse: 更新结果
        """
        async with get_async_session() as session:
            result = await session.execute(
                select(ContentTopic).where(ContentTopic.id == id)
            )
            topic = result.scalar_one_or_none()

            if not topic:
                return error("话题不存在")

            # 如果设置了分类ID，验证分类是否存在
            if category_id is not None:
                category_result = await session.execute(
                    select(ContentCategory).where(
                        ContentCategory.id == category_id,
                        ContentCategory.status == 1,
                    )
                )
                category = category_result.scalar_one_or_none()
                if not category:
                    return error("指定的分类不存在或已禁用")

            # 更新分类
            topic.category_id = category_id
            await session.commit()

            return success(
                {
                    "id": topic.id,
                    "category_id": topic.category_id,
                    "message": "分类更新成功",
                }
            )

    async def batch_update_category(
        self, id_array: list[int], category_id: int | None
    ) -> JSONResponse:
        """批量更新话题分类

        Args:
            id_array: 话题ID列表
            category_id: 分类ID（None 表示清空分类）

        Returns:
            JSONResponse: 更新结果
        """
        if not id_array:
            return error("请选择要更新的话题")

        async with get_async_session() as session:
            # 如果设置了分类ID，验证分类是否存在
            if category_id is not None:
                category_result = await session.execute(
                    select(ContentCategory).where(
                        ContentCategory.id == category_id,
                        ContentCategory.status == 1,
                    )
                )
                category = category_result.scalar_one_or_none()
                if not category:
                    return error("指定的分类不存在或已禁用")

            # 查询所有要更新的话题
            result = await session.execute(
                select(ContentTopic).where(ContentTopic.id.in_(id_array))
            )
            topics = result.scalars().all()

            if not topics:
                return error("未找到要更新的话题")

            # 批量更新分类
            updated_count = 0
            for topic in topics:
                topic.category_id = category_id
                updated_count += 1

            await session.commit()

            return success(
                {
                    "updated_count": updated_count,
                    "category_id": category_id,
                    "message": f"成功更新 {updated_count} 个话题的分类",
                }
            )

    async def generate_and_update_description(
        self, id: int, model: str | None = None
    ) -> JSONResponse:
        """AI 生成并更新话题描述

        Args:
            id: 话题ID
            model: AI 模型（可选）

        Returns:
            JSONResponse: 生成并更新结果
        """
        from Modules.content.services.ai_service import AIService

        # 1. 获取话题信息
        async with get_async_session() as session:
            result = await session.execute(
                select(ContentTopic).where(ContentTopic.id == id)
            )
            topic = result.scalar_one_or_none()

            if not topic:
                return error("话题不存在")

            if not topic.title:
                return error("话题标题为空，无法生成描述")

            title = topic.title

        # 2. 调用 AI 生成描述
        ai_service = AIService()
        ai_result = await ai_service.generate_description(title, model)

        if ai_result.status_code != 200:
            return ai_result

        # 3. 提取生成的描述
        ai_data = json.loads(ai_result.body.decode())
        description = ai_data.get("data", {}).get("description", "")

        if not description:
            return error("AI 生成的描述为空")

        # 4. 更新数据库
        async with get_async_session() as session:
            result = await session.execute(
                select(ContentTopic).where(ContentTopic.id == id)
            )
            topic = result.scalar_one_or_none()

            if topic:
                topic.description = description
                await session.commit()

        # 5. 返回结果
        return success(
            {
                "id": id,
                "title": title,
                "description": description,
                "model": ai_data.get("data", {}).get("model"),
                "message": "描述生成并保存成功",
            }
        )

    async def generate_and_update_category(
        self, id: int, model: str | None = None
    ) -> JSONResponse:
        """AI 生成并更新话题分类（支持两级分类和自动创建）

        Args:
            id: 话题ID
            model: AI 模型（可选）

        Returns:
            JSONResponse: 生成并更新结果
        """
        from Modules.content.services.ai_service import AIService

        # 1. 获取话题信息
        async with get_async_session() as session:
            result = await session.execute(
                select(ContentTopic).where(ContentTopic.id == id)
            )
            topic = result.scalar_one_or_none()

            if not topic:
                return error("话题不存在")

            if not topic.title:
                return error("话题标题为空，无法生成分类")

            title = topic.title
            description = topic.description

        # 2. 调用 AI 生成分类名称（AI 只返回分类名称，不做任何决策）
        ai_service = AIService()
        ai_result = await ai_service.generate_category(
            title=title, categories=[], model=model, description=description
        )

        if ai_result.status_code != 200:
            return ai_result

        # 3. 解析 AI 返回的分类名称
        ai_data = json.loads(ai_result.body.decode())
        action_data = ai_data.get("data", {})
        parent_category_name = action_data.get("parent_category")
        child_category_name = action_data.get("child_category")

        if not parent_category_name or not child_category_name:
            return error(f"AI 返回的分类名称不完整: {action_data}")

        logger.info(f"[generate_and_update_category] AI 生成的分类: {parent_category_name} > {child_category_name}")

        # 4. 查询或创建父分类
        parent_category = None
        async with get_async_session() as session:
            # 查找父分类（按名称，parent_id 为 None 或 0）
            parent_result = await session.execute(
                select(ContentCategory).where(
                    ContentCategory.name == parent_category_name,
                    (ContentCategory.parent_id == None) | (ContentCategory.parent_id == 0)
                )
            )
            parent_category = parent_result.scalar_one_or_none()

            parent_is_new = False
            if not parent_category:
                # 创建父分类
                parent_slug = self._generate_slug(parent_category_name)
                parent_category = ContentCategory(
                    name=parent_category_name,
                    slug=parent_slug,
                    parent_id=0,  # 一级分类的 parent_id 设为 0
                    status=1,
                    sort=999,
                    created_at=now(),
                    updated_at=now(),
                )
                session.add(parent_category)
                await session.commit()
                await session.refresh(parent_category)
                parent_is_new = True
                logger.info(f"[generate_and_update_category] 创建父分类: {parent_category_name} (ID: {parent_category.id})")
            else:
                logger.info(f"[generate_and_update_category] 使用现有父分类: {parent_category_name} (ID: {parent_category.id})")

        # 5. 查询或创建子分类
        child_category = None
        async with get_async_session() as session:
            # 查找子分类（按名称，parent_id 匹配父分类）
            child_result = await session.execute(
                select(ContentCategory).where(
                    ContentCategory.name == child_category_name,
                    ContentCategory.parent_id == parent_category.id
                )
            )
            child_category = child_result.scalar_one_or_none()

            child_is_new = False
            if not child_category:
                # 创建子分类前，检查 slug 是否已被使用（避免唯一约束冲突）
                child_slug = self._generate_slug(child_category_name)
                slug_check_result = await session.execute(
                    select(ContentCategory).where(ContentCategory.slug == child_slug)
                )
                existing_by_slug = slug_check_result.scalar_one_or_none()

                if existing_by_slug:
                    # slug 已存在，使用现有分类
                    logger.info(
                        f"[generate_and_update_category] 发现 slug '{child_slug}' 已存在，使用现有分类: {existing_by_slug.name} (ID: {existing_by_slug.id})"
                    )
                    child_category = existing_by_slug
                else:
                    # 创建新子分类
                    try:
                        child_category = ContentCategory(
                            name=child_category_name,
                            slug=child_slug,
                            parent_id=parent_category.id,
                            status=1,
                            sort=999,
                            created_at=now(),
                            updated_at=now(),
                        )
                        session.add(child_category)
                        await session.commit()
                        await session.refresh(child_category)
                        child_is_new = True
                        logger.info(
                            f"[generate_and_update_category] 创建子分类: {child_category_name} (ID: {child_category.id})"
                        )
                    except Exception as e:
                        # 处理可能的并发请求导致的重复插入
                        error_msg = str(e)
                        if "1062" in error_msg or "Duplicate entry" in error_msg:
                            logger.warning(
                                f"[generate_and_update_category] 检测到并发插入冲突，尝试查询现有分类: {child_slug}"
                            )
                            await session.rollback()
                            # 重新查询
                            retry_result = await session.execute(
                                select(ContentCategory).where(
                                    ContentCategory.slug == child_slug
                                )
                            )
                            child_category = retry_result.scalar_one_or_none()
                            if child_category:
                                logger.info(
                                    f"[generate_and_update_category] 使用因并发而创建的分类: {child_category.name} (ID: {child_category.id})"
                                )
                            else:
                                raise e
                        else:
                            raise e
            else:
                logger.info(
                    f"[generate_and_update_category] 使用现有子分类: {child_category_name} (ID: {child_category.id})"
                )

        # 6. 更新话题分类
        async with get_async_session() as session:
            result = await session.execute(
                select(ContentTopic).where(ContentTopic.id == id)
            )
            topic = result.scalar_one_or_none()

            if topic:
                topic.category_id = child_category.id
                await session.commit()
                logger.info(f"[generate_and_update_category] 更新话题 {id} 的分类为 {child_category.id}")

        # 7. 构建返回消息
        if child_is_new or parent_is_new:
            message = f"已创建新分类：{parent_category_name} > {child_category_name}"
        else:
            message = f"分类匹配成功：{parent_category_name} > {child_category_name}"

        return success(
            {
                "id": id,
                "category_id": child_category.id,
                "category_name": child_category.name,
                "category_slug": child_category.slug,
                "parent_name": parent_category.name,
                "is_new": child_is_new or parent_is_new,
                "model": action_data.get("model"),
                "message": message,
            }
        )

    def _generate_slug(self, name: str) -> str:
        """生成分类的 slug

        Args:
            name: 分类名称

        Returns:
            str: 生成的 slug（直接使用 name）
        """
        # 直接使用 name 作为 slug
        return name

    async def fetch_zhihu_content(self, id: int) -> JSONResponse:
        """手动抓取知乎问题内容并存储到数据库

        Args:
            id: 话题ID

        Returns:
            JSONResponse: 抓取结果
        """
        # 1. 获取话题信息
        async with get_async_session() as session:
            result = await session.execute(
                select(ContentTopic).where(ContentTopic.id == id)
            )
            topic = result.scalar_one_or_none()

            if not topic:
                return error("话题不存在")

            if not topic.url:
                return error("话题没有关联链接")

            if "zhihu.com" not in topic.url:
                return error("仅支持知乎问题链接")

            url = topic.url
            logger.info(f"[fetch_zhihu_content] 开始抓取知乎内容: {url}")

        # 2. 调用 ZhihuFetcher 抓取内容
        try:
            from Modules.content.services.zhihu_fetcher import ZhihuFetcher

            fetcher = ZhihuFetcher()
            zhihu_content = await fetcher.fetch_question(url)

            if not zhihu_content:
                return error("抓取知乎内容失败，请检查链接是否有效或稍后重试")

            logger.info(
                f"[fetch_zhihu_content] 抓取成功: 标题={zhihu_content.title}, 回答数={len(zhihu_content.answers)}"
            )

        except Exception as e:
            logger.error(f"[fetch_zhihu_content] 抓取异常: {str(e)}")
            return error(f"抓取知乎内容异常: {str(e)}")

        # 3. 存储到数据库
        async with get_async_session() as session:
            result = await session.execute(
                select(ContentTopic).where(ContentTopic.id == id)
            )
            topic = result.scalar_one_or_none()

            if topic:
                # 构建存储的 JSON 数据
                zhihu_data = {
                    "title": zhihu_content.title,
                    "description": zhihu_content.description,
                    "url": zhihu_content.url,
                    "answers": [
                        {
                            "author": answer.get("author", "匿名用户"),
                            "content": answer.get("content", ""),
                        }
                        for answer in zhihu_content.answers
                    ],
                    "fetched_at": now().isoformat(),
                    "answer_count": len(zhihu_content.answers),
                }

                # 存储为 JSON 字符串
                topic.zhihu_content = json.dumps(zhihu_data, ensure_ascii=False)
                topic.zhihu_content_updated_at = now()
                await session.commit()

                logger.info(f"[fetch_zhihu_content] 已存储到数据库: topic_id={id}")

        # 4. 返回结果
        return success(
            {
                "id": id,
                "title": zhihu_content.title,
                "description": zhihu_content.description,
                "url": zhihu_content.url,
                "answers": [
                    {
                        "author": answer.get("author", "匿名用户"),
                        "content": answer.get("content", ""),
                    }
                    for answer in zhihu_content.answers
                ],
                "answer_count": len(zhihu_content.answers),
                "updated_at": format_datetime(topic.zhihu_content_updated_at)
                if topic.zhihu_content_updated_at
                else None,
                "message": f"成功获取知乎内容：{zhihu_content.title}（{len(zhihu_content.answers)} 个回答）",
            }
        )
