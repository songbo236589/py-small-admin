"""
菜单验证器

提供菜单相关的参数验证功能。
"""

from pydantic import Field, field_validator

from ...common.models.base_model import BaseModel


class RuleAddUpdateRequest(BaseModel):
    """菜单添加/更新请求模型"""

    name: str = Field(..., description="菜单名称")
    path: str | None = Field("", description="路由路径")
    component: str | None = Field("", description="组件路径")
    redirect: str | None = Field("", description="重定向路径")
    type: int = Field(1, description="菜单类型:1=模块,2=目录,3=菜单")
    status: int = Field(1, description="侧边栏显示状态:0=隐藏,1=显示")
    icon: str | None = Field("", description="图标")
    pid: int = Field(0, description="父级ID")
    sort: int = Field(1, description="排序")
    target: str | None = Field("", description="链接打开方式：_self/_blank")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v):
        """验证菜单名称"""
        if not v or len(v.strip()) == 0:
            raise ValueError("菜单名称不能为空")
        if len(v) > 100:
            raise ValueError("菜单名称长度不能超过100个字符")
        return v.strip()

    @field_validator("path")
    @classmethod
    def validate_path(cls, v):
        """验证路由路径"""
        if v is None:
            return ""
        if len(v) > 100:
            raise ValueError("路由路径长度不能超过100个字符")
        return v.strip() if v else ""

    @field_validator("component")
    @classmethod
    def validate_component(cls, v):
        """验证组件路径"""
        if v is None:
            return ""
        if len(v) > 100:
            raise ValueError("组件路径长度不能超过100个字符")
        return v.strip() if v else ""

    @field_validator("redirect")
    @classmethod
    def validate_redirect(cls, v):
        """验证重定向路径"""
        if v is None:
            return ""
        if len(v) > 100:
            raise ValueError("重定向路径长度不能超过100个字符")
        return v.strip() if v else ""

    @field_validator("type")
    @classmethod
    def validate_type(cls, v):
        """验证菜单类型"""
        if v not in [1, 2, 3]:
            raise ValueError("菜单类型只能为1(模块)、2(目录)或3(菜单)")
        return v

    @field_validator("status")
    @classmethod
    def validate_status(cls, v):
        """验证状态"""
        if v not in [0, 1]:
            raise ValueError("状态值只能为0(隐藏)或1(显示)")
        return v

    @field_validator("icon")
    @classmethod
    def validate_icon(cls, v):
        """验证图标"""
        if v is None:
            return ""
        if len(v) > 50:
            raise ValueError("图标长度不能超过50个字符")
        return v.strip() if v else ""

    @field_validator("pid")
    @classmethod
    def validate_pid(cls, v):
        """验证父级ID"""
        if v < 0:
            raise ValueError("父级ID不能为负数")
        return v

    @field_validator("sort")
    @classmethod
    def validate_sort(cls, v):
        """验证排序"""
        if v < 0:
            raise ValueError("排序值不能为负数")
        return v

    @field_validator("target")
    @classmethod
    def validate_target(cls, v):
        """验证链接打开方式"""
        if v is None:
            return ""
        v = v.strip()
        if v and v not in ["_self", "_blank"]:
            raise ValueError("链接打开方式只能为_self或_blank")
        return v
