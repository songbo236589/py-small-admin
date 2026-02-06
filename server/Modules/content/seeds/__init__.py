"""
Content 模块种子数据入口

该模块负责运行Content模块的所有种子数据。
"""


def run_seeds(env="development"):
    """运行所有种子数据"""
    from .content_seed import seed_content_data

    # 根据环境执行不同的种子数据
    if env == "development":
        # 开发环境：创建完整的测试数据
        seed_content_data()
    elif env == "production":
        # 生产环境：只创建必要的初始数据
        seed_content_data()
    elif env == "test":
        # 测试环境：创建特定的测试数据
        seed_content_data()
