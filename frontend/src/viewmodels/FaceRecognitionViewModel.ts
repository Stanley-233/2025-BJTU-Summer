import {ref, onMounted, onBeforeUnmount, nextTick, inject} from 'vue'
import { DefaultApi, Configuration } from '../api/generated'
import { blobToBase64 } from '../util/base64'
import CryptoJS from "crypto-js";

export default function useFaceRecognition() {
  // inject global bubble from root provider
  const showGlobalBubble = inject<(msg: string) => void>('showGlobalBubble')
  const videoRef = ref<HTMLVideoElement | null>(null)
  const hasPermission = ref(false)
  const recording = ref(false)
  const countdown = ref(0)
  const isLoading = ref(false)
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
      showGlobalBubble
        ? showGlobalBubble('无法获取摄像头权限，请检查浏览器设置。')
        : alert('无法获取摄像头权限，请检查浏览器设置。')
    }
  }

  function cleanup() {
    if (stream) {
      stream.getTracks().forEach(track => track.stop())
    }
  }

  async function startCapture() {
    if (!stream) {
      showGlobalBubble
        ? showGlobalBubble('摄像头未就绪')
        : alert('摄像头未就绪')
      return
    }
    // 初始化倒计时并开始采集
    recording.value = true
    countdown.value = 2
    const ct = setInterval(() => {
      if (countdown.value > 0) countdown.value--
      if (countdown.value <= 0) clearInterval(ct)
    }, 1000)
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
      countdown.value = 0
      // 等待API响应，显示识别中
      isLoading.value = true
      const videoBlob = new Blob(chunks, { type: 'video/mp4' })
      try {
        const dataUrl = await blobToBase64(videoBlob)
        let base64 = dataUrl.split(',')[1]
        base64 = CryptoJS.AES.encrypt(base64, 'BrPz0VgQzNmhw1KmHfEyUFu1DHnq0schBijdSm0P_K0=').toString();
        const api = new DefaultApi(new Configuration({
          basePath: 'http://127.0.0.1:8000',
          accessToken: sessionStorage.getItem('token') ? () => sessionStorage.getItem('token')! : undefined,
        }))
        const response = await api.checkFaceDataCheckFacePost({ face_data: base64 })
        const token = response.data?.token
        sessionStorage.setItem('token', token)
        let user_name = response.data?.user.username
        if (showGlobalBubble) {
          showGlobalBubble("人脸识别成功，欢迎回来，" + user_name + "！");
        } else {
          alert("人脸识别成功，欢迎回来，" + user_name + "！");
        }
        window.location.assign('/console')
      } catch (error: any) {
        console.error(error)
        const status = error.response?.status
        if (status === 404) {
          showGlobalBubble ?
            showGlobalBubble("人脸识别失败：用户不存在或人脸数据不存在") :
            alert("人脸识别失败：用户不存在或人脸数据不存在")
        } else if (status === 402) {
          showGlobalBubble ?
            showGlobalBubble(error.response.data?.detail || "活体检测失败") :
            alert(error.response.data?.detail || "活体检测失败")
        } else if (status === 406) {
          showGlobalBubble ?
            showGlobalBubble("人脸识别失败：同时出现两人") :
            alert("人脸识别失败：同时出现两人")
        } else {
          showGlobalBubble ?
            showGlobalBubble("服务器内部错误" + error.message) :
            alert("服务器内部错误")
        }
      } finally {
        isLoading.value = false
      }
    }
  }

  onMounted(init)
  onBeforeUnmount(cleanup)

  return { videoRef, hasPermission, recording, startCapture, countdown, isLoading }
}
