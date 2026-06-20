def run_task(runner, observation):
    """
    独立包装：日常登录任务逻辑。
    由于日常登录上线即自动完成，它会直接在日常任务列表中由通用框架完成一键领奖与 claimed 销账。
    因此该模块无需任何具体的子页面控制代码，直接返回 None 使其回退至通用领奖逻辑。
    """
    return None
