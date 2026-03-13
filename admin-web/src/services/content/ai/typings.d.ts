declare namespace API {
  // AI 模型信息
  type AIModel = {
    name: string;
    label?: string;
    description?: string;
    size: number;
    modified_at: string;
  };

  // 获取模型列表响应
  type GetModelsResponse = {
    models: AIModel[];
    default_model: string;
  };

  // AI 生成文章请求
  type AIGenerateArticleRequest = {
    id: number;
    mode: 'title' | 'description' | 'full';
    model?: string;
    variant_index?: number;
  };

  // AI 生成文章响应
  type AIGenerateArticleResponse = {
    topic_id: number;
    mode: string;
    title?: string;
    content: string;
    summary?: string;
    tag_ids?: number[];
    tags?: Array<{ id: number; name: string; color?: string }>;
    model: string;
  };
}
