import { ref, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { DefaultApi, Configuration } from '../api/generated'
import { blobToBase64 } from '../util/base64'

export default function useFaceRecognition() {
  const videoRef = ref<HTMLVideoElement | null>(null)
  const hasPermission = ref(false)
  const recording = ref(false)
  let stream: MediaStream | null = null
  let mediaRecorder: MediaRecorder | null = null

  async function init() {
    try {
      stream = await navigator.mediaDevices.getUserMedia({ video: true })
      hasPermission.value = true
      await nextTick()
      if (videoRef.value) {
        videoRef.value.srcObject = stream
        videoRef.value.play?.()
      }
    } catch (e) {
      hasPermission.value = false
      alert('无法获取摄像头权限，请检查浏览器设置。')
    }
  }

  function cleanup() {
    if (stream) {
      stream.getTracks().forEach(track => track.stop())
    }
  }

  async function startCapture() {
    if (!stream) {
      alert('摄像头未就绪')
      return
    }
    recording.value = true
    const chunks: Blob[] = []
    try {
      mediaRecorder = new MediaRecorder(stream as MediaStream, { mimeType: 'video/mp4' })
    } catch {
      mediaRecorder = new MediaRecorder(stream as MediaStream)
    }
    mediaRecorder.ondataavailable = (e: BlobEvent) => chunks.push(e.data)
    mediaRecorder.start()
    setTimeout(() => mediaRecorder?.stop(), 2000)
    mediaRecorder.onstop = async () => {
      recording.value = false
      const videoBlob = new Blob(chunks, { type: 'video/mp4' })
      try {
        const dataUrl = await blobToBase64(videoBlob)
        const base64 = dataUrl.split(',')[1]
        const api = new DefaultApi(new Configuration({
          basePath: 'http://127.0.0.1:8000',
          accessToken: sessionStorage.getItem('token') ? () => sessionStorage.getItem('token')! : undefined,
        }))
        await api.checkFaceDataCheckFacePost({ face_data: base64 })
        alert('识别成功')
      } catch (error) {
        console.error(error)
        alert('识别失败，请重试')
      }
    }
  }

  onMounted(init)
  onBeforeUnmount(cleanup)

  return { videoRef, hasPermission, recording, startCapture }
}
