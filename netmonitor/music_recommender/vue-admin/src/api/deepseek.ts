import axios from 'axios';

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

interface ChatResponse {
  message: string;
  error?: string;
}

const DEEPSEEK_API_URL = 'https://api.deepseek.com/v1/chat/completions';  // 这里需要替换为实际的 API 地址

class DeepseekService {
  private apiKey: string;

  constructor(apiKey: string) {
    this.apiKey = apiKey;
  }

  async chat(messages: Message[]): Promise<ChatResponse> {
    try {
      const response = await axios.post(
        DEEPSEEK_API_URL,
        {
          messages,
          model: 'deepseek-chat',  // 根据实际 API 文档调整
          temperature: 0.7,
          max_tokens: 2000
        },
        {
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${this.apiKey}`
          }
        }
      );

      return {
        message: response.data.choices[0].message.content
      };
    } catch (error: any) {
      console.error('Deepseek API Error:', error);
      return {
        message: '',
        error: error.response?.data?.error?.message || '请求失败，请稍后重试'
      };
    }
  }
}

// 创建服务实例
const deepseekService = new DeepseekService(import.meta.env.VITE_DEEPSEEK_API_KEY || '');

export default deepseekService; 