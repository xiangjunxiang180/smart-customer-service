const app = getApp()

Page({
  data: {
    messages: [],
    inputValue: '',
    isManual: false,
    showFaq: true,
    faqList: []
  },

  onLoad() {
    // 生成唯一用户ID并保存到本地
    const userId = wx.getStorageSync('userId') || 'user_' + Date.now()
    wx.setStorageSync('userId', userId)
    this.setData({ userId })
    
    // 获取常见问题列表
    this.getFaq()
    
    // 获取用户聊天历史
    this.getChatHistory()
  },

  getFaq() {
    wx.request({
      url: 'http://10.110.183.52:8000/api/faq',
      method: 'GET',
      timeout: 15000, // 增加超时时间到15秒
      success: (res) => {
        if (res.statusCode === 200) {
          this.setData({ faqList: res.data.faq })
        }
      },
      fail: () => {
        wx.showToast({
          title: '获取常见问题失败',
          icon: 'none'
        })
      }
    })
  },

  getChatHistory() {
    const userId = this.data.userId
    wx.request({
      url: `http://10.110.183.52:8000/api/history/${userId}`,
      method: 'GET',
      timeout: 15000, // 增加超时时间到15秒
      success: (res) => {
        if (res.statusCode === 200) {
          this.setData({ messages: res.data.history })
        }
      },
      fail: () => {
        wx.showToast({
          title: '获取聊天历史失败',
          icon: 'none'
        })
      }
    })
  },

  onInput(e) {
    this.setData({ inputValue: e.detail.value })
  },

  sendMessage() {
    const content = this.data.inputValue.trim()
    if (!content) return
    
    // 添加用户消息到界面
    const userMessage = {
      role: 'user',
      content: content,
      timestamp: new Date().toISOString()
    }
    
    this.setData({
      messages: [...this.data.messages, userMessage],
      inputValue: '',
      showFaq: false
    })
    
    // 发送请求到后端
    wx.request({
      url: 'http://10.110.183.52:8000/api/chat',
      method: 'POST',
      data: {
        user_id: this.data.userId,
        content: content,
        is_manual: this.data.isManual
      },
      timeout: 15000, // 20秒超时
      success: (res) => {
        if (res.statusCode === 200) {
          // 添加助手回复到界面
          const assistantMessage = {
            role: 'assistant',
            content: res.data.response,
            timestamp: new Date().toISOString(),
            is_manual: this.data.isManual
          }
          
          this.setData({
            messages: [...this.data.messages, assistantMessage]
          })
        } else {
          wx.showToast({
            title: '发送失败，请稍后再试',
            icon: 'none'
          })
        }
      },
      fail: () => {
        wx.showToast({
          title: '网络错误，请检查网络连接',
          icon: 'none'
        })
      }
    })
  },

  switchToManual() {
    this.setData({ isManual: true })
    wx.showToast({
      title: '已为您转接人工客服',
      icon: 'success'
    })
  },

  selectFaq(e) {
    // 点击常见问题自动发送
    const question = e.currentTarget.dataset.question
    this.setData({ inputValue: question })
    this.sendMessage()
  }
})
