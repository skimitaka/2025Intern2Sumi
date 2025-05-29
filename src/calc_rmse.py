import numpy as np
from scipy.interpolate import interp1d

def calc_rmse(radar_est_time, radar_est_ibi, ecg_time, ecg_ibi, calc_intervals=None):
    """
    radar_est_time: (N,) array, radar IBI time
    radar_est_ibi: (N,) array, radar IBI values
    tmpIBIPoly: object with .midTime and .ibi as 1D arrays
    calc_intervals: list of [start, end] intervals. If None, use [0, obj.sum_measure_time]
    レーダに合わせて、ECGのIBIを補間し、RMSEを計算する関数
    """
    interp_dt = 1 / 1000
    polytime_min = np.floor(ecg_time[0] / interp_dt) * interp_dt
    polytime_max = np.ceil(ecg_time[-1] / interp_dt) * interp_dt
    polytime_interp = np.arange(polytime_min,polytime_max, interp_dt)

    interp_func = interp1d(ecg_time, ecg_ibi, kind='linear', bounds_error=False, fill_value="extrapolate")
    polyibi_interp = interp_func(polytime_interp)

    # 前後補間の修正（MATLABと同じ処理）
    first_index = int(np.ceil(ecg_time[0] / interp_dt))
    polyibi_interp[:first_index] = ecg_ibi[0]

    last_index = int(np.floor(ecg_time[-1] / interp_dt))
    polyibi_interp[last_index:] = ecg_ibi[-1]

    if calc_intervals is None:
        calc_intervals = np.array([[polytime_min, polytime_max]])
    else:
        calc_intervals = np.asarray(calc_intervals)

    # 複数区間のインデックスを結合
    calc_index = np.array([], dtype=int)
    for interval in calc_intervals:
        this_index = np.where((radar_est_time >= interval[0]) & (radar_est_time <= interval[1]))[0]
        calc_index = np.concatenate((calc_index, this_index))

    this_IBIradar_est_time = radar_est_time[calc_index]
    # Find the closest indices in polytime_interp for each value in this_IBIradar_est_time
    reference_index = np.array([np.argmin(np.abs(polytime_interp - t)) for t in this_IBIradar_est_time])
    # reference_index = np.round(this_IBIradar_est_time / interp_dt).astype(int)
    this_polyibi_interp = polyibi_interp[reference_index]
    this_IBITpl_value = radar_est_ibi[calc_index]

    IBI_diff = this_IBITpl_value - this_polyibi_interp
    rmse_value = np.sqrt(np.mean((this_IBITpl_value - this_polyibi_interp) ** 2))

    return rmse_value, IBI_diff