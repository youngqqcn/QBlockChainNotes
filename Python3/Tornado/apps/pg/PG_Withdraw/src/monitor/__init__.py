from src.config.constant import WithdrawStatus


class SubMonitorFuncResponse:
    block_height =  0
    transaction_status = WithdrawStatus.transaction_status.NOTYET
    confirmations = 0
    tx_hash = ''
    block_time = 0


class NotifyFuncResponse:
    is_notify_successed = False
