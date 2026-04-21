import { defineStore } from 'pinia'

export const useAlarmStore = defineStore('alarm', {
  state: () => ({
    alarmList: [], // 实时告警数据
    stats: { total: 0, critical: 0 } // 统计数字
  }),
  actions: {
    // 模拟接收后端推送的实时告警
    addAlarm(alarm) {
      this.alarmList.unshift({
        id: Date.now(),
        ...alarm,
        time: new Date().toLocaleTimeString()
      })
      this.stats.total++
    }
  }
})