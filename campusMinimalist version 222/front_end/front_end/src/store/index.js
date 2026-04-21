import { createStore } from 'vuex'

function getDefaultUiMetrics() {
  return {
    fps: '58-60 FPS',
    latency: '12 ms',
    resolution: '1080P',
    streamStatus: '实时流稳定'
  }
}

export default createStore({
  state: {
    cameras: [
      { id: 1, name: '正门入口', location: 'A区', status: 'online', alert: true },
      { id: 2, name: '停车场B', location: 'B区', status: 'online', alert: false },
      { id: 3, name: '走廊C-1', location: 'C区', status: 'online', alert: false },
      { id: 4, name: '仓库入口', location: 'D区', status: 'warning', alert: false },
      { id: 5, name: '办公区域', location: 'E区', status: 'online', alert: false },
      { id: 6, name: '应急通道', location: 'F区', status: 'offline', alert: false }
    ],

    alerts: [
      { id: 1, type: '打架斗殴', camera: '正门入口', time: '03:01:22', level: 'critical', handled: false },
      { id: 2, type: '人员跌倒', camera: '走廊C-1', time: '02:58:10', level: 'high', handled: false },
      { id: 3, type: '闯入禁区', camera: '仓库入口', time: '02:45:33', level: 'high', handled: true },
      { id: 4, type: '吸烟行为', camera: '停车场B', time: '02:30:05', level: 'medium', handled: true },
      { id: 5, type: '人员聚集', camera: '办公区域', time: '02:15:48', level: 'low', handled: true }
    ],

    logs: [
      { id: 1, time: '03:01:22', camera: '正门入口', behavior: '打架斗殴', confidence: 96.3, persons: 2, status: '未处理' },
      { id: 2, time: '02:58:10', camera: '走廊C-1', behavior: '人员跌倒', confidence: 89.7, persons: 1, status: '未处理' },
      { id: 3, time: '02:45:33', camera: '仓库入口', behavior: '闯入禁区', confidence: 94.1, persons: 1, status: '已处理' },
      { id: 4, time: '02:30:05', camera: '停车场B', behavior: '吸烟行为', confidence: 87.2, persons: 1, status: '已处理' },
      { id: 5, time: '02:15:48', camera: '办公区域', behavior: '人员聚集', confidence: 78.5, persons: 5, status: '已处理' },
      { id: 6, time: '01:55:21', camera: '应急通道', behavior: '奔跑行为', confidence: 82.0, persons: 1, status: '已处理' }
    ],

    stats: {
      totalToday: 23,
      unhandled: 2,
      onlineCameras: 5,
      totalCameras: 6
    },

    uiMetrics: getDefaultUiMetrics(),

    mainStream: {
      name: '校园危险行为智能识别系统',
      mode: '单路视频准实时分析'
    },

    selectedCamera: 1
  },

  mutations: {
    SET_SELECTED_CAMERA(state, id) {
      state.selectedCamera = id
    },

    HANDLE_ALERT(state, id) {
      const alert = state.alerts.find(item => item.id === id)
      if (alert) {
        alert.handled = true
      }

      state.stats.unhandled = state.alerts.filter(item => !item.handled).length
    },

    UPDATE_LOG_STATUS(state, payload) {
      const target = state.logs.find(item => item.id === payload.id)
      if (target) {
        target.status = payload.status
      }
    },

    ADD_LOG(state, log) {
      state.logs.unshift(log)
      state.stats.totalToday = state.logs.length
      state.stats.unhandled = state.logs.filter(item => item.status === '未处理').length
    },

    UPDATE_STATS(state, stats) {
      state.stats = {
        ...state.stats,
        ...stats
      }
    },

    SET_UI_METRICS(state, metrics) {
      state.uiMetrics = {
        ...getDefaultUiMetrics(),
        ...(state.uiMetrics || {}),
        ...(metrics || {})
      }
    }
  },

  actions: {
    selectCamera({ commit }, id) {
      commit('SET_SELECTED_CAMERA', id)
    },

    handleAlert({ commit, state }, id) {
      commit('HANDLE_ALERT', id)

      const currentAlert = state.alerts.find(item => item.id === id)
      if (!currentAlert) return

      const targetLog = state.logs.find(
        item =>
          item.camera === currentAlert.camera &&
          item.behavior === currentAlert.type
      )

      if (targetLog) {
        commit('UPDATE_LOG_STATUS', {
          id: targetLog.id,
          status: '已处理'
        })
      }
    },

    updateUiMetrics({ commit }, metrics) {
      commit('SET_UI_METRICS', metrics)
    }
  },

  getters: {
    unhandledAlerts: state => state.alerts.filter(item => !item.handled),
    onlineCameras: state => state.cameras.filter(item => item.status === 'online'),
    safeUiMetrics: state => state.uiMetrics || getDefaultUiMetrics(),
    selectedCameraInfo: state =>
      state.cameras.find(item => item.id === state.selectedCamera) || state.cameras[0] || null
  }
})
