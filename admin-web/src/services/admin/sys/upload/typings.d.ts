declare namespace API {
  // 列表参数
  type AdminUploadList = {
    id: number;
    url: string;
    thumbnail_url: string;
    original_name: string;
    filename: string;
    file_path: string;
    file_size: number;
    mime_type: string;
    file_ext: string;
    file_hash: string | null;
    storage_type: 'local' | 'aliyun_oss' | 'tencent_oss' | 'qiniu_oss';
    file_type: 'image' | 'document' | 'video' | 'audio' | 'other';
    admin_id: number | null;
    width: number;
    height: number;
    duration: number;
    thumbnail_filename: string | null;
    thumbnail_path: string | null;
    extra_info: string | null;
    created_at: string;
  };

  // 上传文件接口参数
  type AdminUploadFile = {
    file_type: 'image' | 'document' | 'video' | 'audio' | 'other';
    file: File;
  };
}
