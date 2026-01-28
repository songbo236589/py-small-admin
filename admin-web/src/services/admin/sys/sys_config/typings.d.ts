declare namespace API {
  // 列表参数

  type AdminSysConfigForm = {
    site_name: string;
    site_description: string;
    site_keywords: string;
    site_logo?: number;
    site_logo_data?: API.AdminUploadList[];
    site_favicon?: number;
    site_favicon_data?: API.AdminUploadList[];
    copyright: string;
    site_content: string;
  };
  type AdminEmailConfigForm = {
    smtp_host: string;
    smtp_port: string;
    smtp_username: string;
    smtp_password: string;
    mail_from_address: string;
    mail_from_name: string;
  };
  type TestEmailForm = {
    to_emails: string[] | null | string;
    subject: string;
    content: string;
    content_type: 'html' | 'plain';
    attachments: string;
  };
  type AdminUploadConfigForm = {
    upload_storage_type: string;
    upload_image_max_size: number;
    upload_image_allowed_types: string[];
    upload_video_max_size: number;
    upload_video_allowed_types: string[];
    upload_document_max_size: number;
    upload_document_allowed_types: string[];
    upload_audio_max_size: number;
    upload_audio_allowed_types: string[];
    upload_compress_enabled: boolean;
    upload_compress_quality: number;
    upload_compress_max_width: number;
    upload_compress_max_height: number;
    upload_watermark_enabled: boolean;
    upload_watermark_type: string;
    upload_watermark_text: string;
    upload_watermark_position: string;
    upload_watermark_opacity: string;
    upload_watermark_font_size: number;
    upload_watermark_font_color: string;
    upload_watermark_font_path: string;
    upload_watermark_image?: number;
    upload_watermark_image_data?: API.AdminUploadList[];
    upload_watermark_image_scale: string;
    upload_watermark_margin: number;
    upload_thumbnail_enabled: boolean;
    upload_thumbnail_width: number;
    upload_thumbnail_height: number;
    upload_thumbnail_quality: number;
    upload_thumbnail_suffix: string;
  };
}
