import axios from 'axios'

const request = axios.create({
  baseURL: '/api',
  timeout: 15000
})

export const getApiInfo = () => request.get('/')

export const getStatus = () => request.get('/status')

export const getLogs = (type = 'app', lines = 50) =>
    request.get('/logs', {
      params: { type, lines }
    })

// ==================== 实时流 ====================
export const getVideoFeedUrl = (source = '0') =>
    `/api/video_feed?source=${encodeURIComponent(source)}`

export const stopStream = (sourceId) =>
    request.get('/stop', {
      params: { source_id: sourceId }
    })

export const stopAllStreams = () => request.get('/stop_all')

// ==================== 上传任务 ====================
export const uploadVideo = (file, onProgress) => {
  const formData = new FormData()
  formData.append('video', file)

  return request.post('/upload_video', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    },
    timeout: 0,
    onUploadProgress: (progressEvent) => {
      if (progressEvent.total && onProgress) {
        const percent = Math.round((progressEvent.loaded * 100) / progressEvent.total)
        onProgress(percent)
      }
    }
  })
}

export const getTaskStatus = (taskId) =>
    request.get('/task_status', {
      params: { task_id: taskId }
    })

export const getTasks = () => request.get('/tasks')

export const stopTask = (taskId) =>
    request.get('/stop_task', {
      params: { task_id: taskId }
    })

export const getResultVideoUrl = (taskId) =>
    `/api/result_video?task_id=${encodeURIComponent(taskId)}`

export default request