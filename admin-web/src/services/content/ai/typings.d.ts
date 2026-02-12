declare namespace API {
  // Ollama 模型信息
  type OllamaModel = {
    name: string;
    size: number;
    modified_at: string;
  };

  // 获取模型列表响应
  type GetModelsResponse = {
    models: OllamaModel[];
  };

  // AI 生成文章请求
  type AIGenerateArticleRequest = {
    id: number;
    mode: 'title' | 'description' | 'full';
    title: string;
    description?: string;
    model?: string;
  };

  // AI 生成文章响应
  type AIGenerateArticleResponse = {
    topic_id: number;
    mode: string;
    content: string;
    model: string;
  };
}
