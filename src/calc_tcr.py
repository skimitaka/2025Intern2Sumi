import numpy as np
from scipy.interpolate import interp1d

def calc_tcr(ibi_time, ibi_value, ecg_time, ecg_ibi, TCR_dt, ERROR_TIME):
    """
    TCR（Time Coverage Rate）を計算する関数

    Parameters:
    - ibi_time : array-like (N,)
        レーダー側のIBIの時間
    - ibi_value : array-like (N,)
        レーダー側のIBIの値
    - ecg_time : array-like (M,)
        ECGのIBIの時間
    - ecg_ibi : array-like (M,)
        ECGのIBIの値
    - TCR_dt : float
        TCRの評価単位（秒）
    - ERROR_TIME : float
        IBIの差がこの値以下なら一致とみなす（秒）

    Returns:
    - tcr : float
        Time Coverage Rate（%）
    """

    # TCRの評価点数
    TCR_intervalN = int(np.floor((ecg_time[-1] - ecg_time[0]) / TCR_dt))
    start_TCR_dt = TCR_dt / 2
    xq = np.arange(
        ecg_time[0] + start_TCR_dt,
        ecg_time[0] + start_TCR_dt + TCR_intervalN * TCR_dt,
        TCR_dt
    )

    # 線形補間
    interp_func = interp1d(ecg_time, ecg_ibi, kind='linear', bounds_error=False, fill_value="extrapolate")
    vq = interp_func(xq)
    vq[0] = ecg_ibi[0]
    vq[-1] = ecg_ibi[-1]

    # 各区間で一致するデータがあるか判定
    each_time_cover = np.zeros(TCR_intervalN, dtype=bool)

    for i in range(TCR_intervalN):
        start_interval = xq[i] - TCR_dt / 2
        end_interval = xq[i] + TCR_dt / 2

        ibis_in_range = ibi_value[(ibi_time >= start_interval) & (ibi_time < end_interval)]
        if ibis_in_range.size > 0:
            within_error = np.abs(ibis_in_range - vq[i]) < ERROR_TIME
            each_time_cover[i] = np.any(within_error)

    tcr = round(np.sum(each_time_cover) * 100 / TCR_intervalN, 2)
    return tcr
