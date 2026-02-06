import { file as uploadFile } from '@/services/admin/sys/upload/api';
import { AudioOutlined, PlayCircleOutlined } from '@ant-design/icons';
import type { ProFormInstance } from '@ant-design/pro-components';
import { ProForm } from '@ant-design/pro-components';
import { Editor } from '@tinymce/tinymce-react';
import { Button, message, Modal } from 'antd';
import React, { useEffect, useRef, useState } from 'react';
import type { Editor as TinyMCEEditor } from 'tinymce/tinymce';
import AudiosUpload from '../Upload/AudiosUpload';
import ImageUpload from '../Upload/ImageUpload';
import VideoUpload from '../Upload/VideoUpload';
import type { AdminUploadList } from '../Upload/types';

export interface ProFormTinyMCEProps {
  name: string;
  label?: string;
  placeholder?: string;
  rules?: any[];
  disabled?: boolean;
  required?: boolean;
  height?: number;
  init?: any;
  formRef?: React.RefObject<ProFormInstance | null>;
}

const ProFormTinyMCE: React.FC<ProFormTinyMCEProps> = ({
  name,
  label,
  placeholder = '请输入内容...',
  rules,
  disabled = false,
  required = false,
  height = 500,
  init = {},
  formRef,
}) => {
  const editorRef = useRef<TinyMCEEditor | null>(null);
  const hiddenInputRef = useRef<HTMLInputElement>(null);
  const [editorInitialized, setEditorInitialized] = useState(false);
  const [selectedImage, setSelectedImage] = useState<AdminUploadList | undefined>(undefined);
  const [imagePickerCallback, setImagePickerCallback] = useState<((url: string) => void) | null>(
    null,
  );
  const [shouldOpenImageUpload, setShouldOpenImageUpload] = useState(false);
  const openImageUploadRef = useRef<(() => void) | null>(null);
  const [selectedVideo, setSelectedVideo] = useState<AdminUploadList | undefined>(undefined);
  const [videoPickerCallback, setVideoPickerCallback] = useState<((url: string) => void) | null>(
    null,
  );
  const [shouldOpenVideoUpload, setShouldOpenVideoUpload] = useState(false);
  const openVideoUploadRef = useRef<(() => void) | null>(null);
  const [selectedAudio, setSelectedAudio] = useState<AdminUploadList | undefined>(undefined);
  const [audioPickerCallback, setAudioPickerCallback] = useState<((url: string) => void) | null>(
    null,
  );
  const [shouldOpenAudioUpload, setShouldOpenAudioUpload] = useState(false);
  const openAudioUploadRef = useRef<(() => void) | null>(null);
  const [mediaTypeModalVisible, setMediaTypeModalVisible] = useState(false);

  /**
   * 处理内容中的 blob URL，上传并替换为真实 URL
   */
  const handleBlobUrls = async (editor: TinyMCEEditor, content: string) => {
    const blobRegex = /src="blob:([^"]+)"/g;
    const matches = [];
    let match;

    // 提取所有 blob URL
    while ((match = blobRegex.exec(content)) !== null) {
      matches.push({
        fullMatch: match[0],
        blobUrl: match[1],
      });
    }

    if (matches.length === 0) {
      return;
    }
    console.log(content, matches);
    // 上传所有 blob 图片
    const uploadPromises = matches.map(async ({ fullMatch, blobUrl }) => {
      try {
        const response = await fetch(`blob:${blobUrl}`);
        const blob = await response.blob();

        // 根据 MIME 类型推断文件扩展名
        const mimeType = blob.type || 'image/jpeg';
        const extensionMap: Record<string, string> = {
          // 图片类型
          'image/jpeg': 'jpg',
          'image/jpg': 'jpg',
          'image/png': 'png',
          'image/gif': 'gif',
          'image/webp': 'webp',
          'image/bmp': 'bmp',
          // 视频类型
          'video/mp4': 'mp4',
          'video/webm': 'webm',
          'video/ogg': 'ogg',
          'video/quicktime': 'mov',
          'video/x-msvideo': 'avi',
          'video/x-matroska': 'mkv',
          // 音频类型
          'audio/mpeg': 'mp3',
          'audio/mp3': 'mp3',
          'audio/wav': 'wav',
          'audio/ogg': 'ogg',
          'audio/aac': 'aac',
          'audio/flac': 'flac',
          'audio/x-m4a': 'm4a',
        };
        const extension =
          extensionMap[mimeType] ||
          (mimeType.startsWith('video/') ? 'mp4' : mimeType.startsWith('audio/') ? 'mp3' : 'jpg');

        // 判断文件类型
        const isVideo = mimeType.startsWith('video/');
        const isAudio = mimeType.startsWith('audio/');
        const fileType = isVideo ? 'video' : isAudio ? 'audio' : 'image';

        // 生成文件名
        const fileName = `${fileType}_${Date.now()}.${extension}`;

        // 创建 File 对象
        const file = new File([blob], fileName, { type: mimeType });

        const uploadResult = await uploadFile({
          file: file,
          file_type: fileType,
        } as any);

        if (uploadResult.code === 200 && uploadResult.data?.url) {
          return {
            fullMatch,
            blobUrl,
            realUrl: uploadResult.data.url,
          };
        } else {
          console.error('上传失败:', uploadResult);
          return {
            fullMatch,
            blobUrl,
            realUrl: undefined,
          };
        }
      } catch (error) {
        console.error('上传 blob 失败:', error);
        return {
          fullMatch,
          blobUrl,
          realUrl: undefined,
        };
      }
    });

    // 等待所有上传完成
    const results = await Promise.all(uploadPromises);

    // 替换内容中的 blob URL
    let newContent = content;
    results.forEach((result) => {
      if (result.realUrl) {
        // 替换完整的 src="blob:..." 部分
        newContent = newContent.replace(result.fullMatch, `src="${result.realUrl}"`);
      } else {
        message.error('上传失败');
      }
    });

    // 更新编辑器内容
    editor.setContent(newContent);
  };

  // 处理编辑器初始化
  const handleEditorInit = (evt: any, editor: TinyMCEEditor) => {
    editorRef.current = editor;
    setEditorInitialized(true);

    // 如果表单有初始值，设置到编辑器
    if (formRef?.current) {
      const initialValue = formRef.current.getFieldValue(name);
      if (initialValue) {
        editor.setContent(initialValue);
      }
    }

    // 监听内容变化，检测并上传 blob URL
    editor.on('SetContent', (e: any) => {
      const content = e.content;
      if (content && content.includes('blob:')) {
        handleBlobUrls(editor, content);
      }
    });

    // 监听粘贴后处理
    editor.on('PastePostProcess', (e: any) => {
      const content = e.content;
      if (content && content.includes('blob:')) {
        handleBlobUrls(editor, content);
      }
    });
  };

  // 处理内容变化
  const handleEditorChange = (content: string) => {
    if (formRef?.current) {
      formRef.current.setFieldsValue({
        [name]: content,
      });
    }
  };

  // 监听表单值变化，同步到编辑器
  useEffect(() => {
    if (formRef?.current && editorInitialized && editorRef.current) {
      const currentValue = formRef.current.getFieldValue(name);
      if (currentValue !== undefined) {
        const editorContent = editorRef.current.getContent();
        if (editorContent !== currentValue) {
          editorRef.current.setContent(currentValue);
        }
      }
    }
  }, [formRef, name, editorInitialized]);

  /**
   * 处理图片选择变化
   */
  const handleImageChange = (files?: AdminUploadList | AdminUploadList[]) => {
    // 转换为数组处理
    const fileList = Array.isArray(files) ? files : files ? [files] : [];
    const file = fileList[0];

    setSelectedImage(file);
    if (file && imagePickerCallback) {
      imagePickerCallback(file.url);
    }
    // 重置打开状态
    setShouldOpenImageUpload(false);
  };

  /**
   * 处理视频选择变化
   */
  const handleVideoChange = (files?: AdminUploadList | AdminUploadList[]) => {
    // 转换为数组处理
    const fileList = Array.isArray(files) ? files : files ? [files] : [];
    const file = fileList[0];

    setSelectedVideo(file);
    if (file && videoPickerCallback) {
      videoPickerCallback(file.url);
    }
    // 重置打开状态
    setShouldOpenVideoUpload(false);
  };

  /**
   * 处理音频选择变化
   */
  const handleAudioChange = (files?: AdminUploadList | AdminUploadList[]) => {
    // 转换为数组处理
    const fileList = Array.isArray(files) ? files : files ? [files] : [];
    const file = fileList[0];

    setSelectedAudio(file);
    if (file && audioPickerCallback) {
      audioPickerCallback(file.url);
    }
    // 重置打开状态
    setShouldOpenAudioUpload(false);
  };

  // 合并配置
  const mergedInit = {
    height,
    menubar: true,
    toolbar_mode: 'wrap',
    toolbar_location: 'top',
    language: 'zh_CN',
    language_url: '/tinymce/langs/zh_CN.js',
    placeholder,
    license_key: 'gpl',
    // 自定义文件选择器 - 用于图片和视频选择
    file_picker_callback: (
      callback: (url: string, meta: any) => void,
      value: string,
      meta: any,
    ) => {
      if (meta.filetype === 'image') {
        // 保存回调函数
        setImagePickerCallback(() => callback);
        // 打开图片上传组件
        if (openImageUploadRef.current) {
          openImageUploadRef.current();
        }
      } else if (meta.filetype === 'media') {
        // 保存回调函数
        setVideoPickerCallback(() => callback);
        setAudioPickerCallback(() => callback);
        // 打开媒体类型选择对话框
        setMediaTypeModalVisible(true);
      }
    },
    image_advtab: false,
    image_uploadtab: false,
    plugins: [
      'accordion',
      'advlist',
      'anchor',
      'autolink',
      'autoresize',
      // 'autosave',
      'charmap',
      'code',
      'codesample',
      'directionality',
      'emoticons',
      'fullscreen',
      'help',
      'image',
      'importcss',
      'insertdatetime',
      'link',
      'lists',
      'media',
      'nonbreaking',
      'pagebreak',
      'preview',
      'quickbars',
      'save',
      'searchreplace',
      'table',
      'visualblocks',
      'visualchars',
      'wordcount',
    ],
    toolbar:
      'undo redo | ' +
      'fullscreen preview code removeformat | ' +
      'image media | ' +
      'alignleft aligncenter alignright alignjustify codesample table | ' +
      'blocks | ' +
      'bold backcolor forecolor| ' +
      'bullist numlist outdent indent | ',

    content_style:
      'body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; font-size: 14px; line-height: 1.6; color: rgba(0, 0, 0, 0.85); }' +
      'p { margin: 0 0 10px 0; }' +
      'img { max-width: 100%; height: auto; }',
    branding: false,
    promotion: false,
    quickbars_insert_toolbar: '', //  "quickimage quicktable"
    ...init,
  };

  return (
    <ProForm.Item
      name={name}
      label={label}
      rules={
        required
          ? [{ required: true, message: `请输入${label || '内容'}` }, ...(rules || [])]
          : rules
      }
      trigger="onBlur"
    >
      <div style={{ border: '1px solid #d9d9d9', borderRadius: '6px', overflow: 'hidden' }}>
        <Editor
          tinymceScriptSrc="/tinymce/tinymce.min.js"
          onInit={handleEditorInit}
          onEditorChange={handleEditorChange}
          disabled={disabled}
          init={mergedInit}
        />
      </div>
      {/* 隐藏的输入框，用于表单验证 */}
      <input
        type="hidden"
        ref={hiddenInputRef}
        name={name}
        onChange={(e) => {
          if (formRef?.current) {
            formRef.current.setFieldsValue({
              [name]: e.target.value,
            });
          }
        }}
      />

      {/* 图片上传组件 - 使用 render 属性隐藏默认 UI，只保留打开弹窗功能 */}
      <ImageUpload
        value={selectedImage}
        onChange={handleImageChange}
        render={(files: any, openModal: () => void) => {
          // 保存打开弹窗的函数
          openImageUploadRef.current = openModal;
          // 当需要打开时，触发打开
          if (shouldOpenImageUpload) {
            setTimeout(() => {
              openModal();
              setShouldOpenImageUpload(false);
            }, 0);
          }
          // 返回 null 隐藏默认 UI
          return null;
        }}
      />

      {/* 视频上传组件 - 使用 render 属性隐藏默认 UI，只保留打开弹窗功能 */}
      <VideoUpload
        value={selectedVideo}
        onChange={handleVideoChange}
        render={(files: any, openModal: () => void) => {
          // 保存打开弹窗的函数
          openVideoUploadRef.current = openModal;
          // 当需要打开时，触发打开
          if (shouldOpenVideoUpload) {
            setTimeout(() => {
              openModal();
              setShouldOpenVideoUpload(false);
            }, 0);
          }
          // 返回 null 隐藏默认 UI
          return null;
        }}
      />

      {/* 音频上传组件 - 使用 render 属性隐藏默认 UI，只保留打开弹窗功能 */}
      <AudiosUpload
        value={selectedAudio}
        onChange={handleAudioChange}
        render={(files: any, openModal: () => void) => {
          // 保存打开弹窗的函数
          openAudioUploadRef.current = openModal;
          // 当需要打开时，触发打开
          if (shouldOpenAudioUpload) {
            setTimeout(() => {
              openModal();
              setShouldOpenAudioUpload(false);
            }, 0);
          }
          // 返回 null 隐藏默认 UI
          return null;
        }}
      />

      {/* 媒体类型选择对话框 */}
      <Modal
        open={mediaTypeModalVisible}
        title="选择媒体类型"
        onCancel={() => {
          setMediaTypeModalVisible(false);
          setVideoPickerCallback(null);
          setAudioPickerCallback(null);
        }}
        footer={null}
        width={400}
        zIndex={1500}
      >
        <div style={{ display: 'flex', gap: '16px', padding: '20px 0' }}>
          <Button
            size="large"
            block
            icon={<PlayCircleOutlined />}
            onClick={() => {
              setMediaTypeModalVisible(false);
              // 打开视频上传
              if (openVideoUploadRef.current) {
                openVideoUploadRef.current();
              }
            }}
          >
            视频
          </Button>
          <Button
            size="large"
            block
            icon={<AudioOutlined />}
            onClick={() => {
              setMediaTypeModalVisible(false);
              // 打开音频上传
              if (openAudioUploadRef.current) {
                openAudioUploadRef.current();
              }
            }}
          >
            音频
          </Button>
        </div>
      </Modal>
    </ProForm.Item>
  );
};

export default ProFormTinyMCE;
