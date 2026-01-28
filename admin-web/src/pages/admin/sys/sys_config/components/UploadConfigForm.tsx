import { ImageUpload } from '@/components';
import { edit, update } from '@/services/admin/sys/sys_config/api';
import type { ProFormInstance } from '@ant-design/pro-components';
import {
  ProForm,
  ProFormCheckbox,
  ProFormDigit,
  ProFormRadio,
  ProFormSelect,
  ProFormSwitch,
  ProFormText,
} from '@ant-design/pro-components';
import { Button, ColorPicker, Form, message, Spin } from 'antd';
import React, { useRef, useState } from 'react';

const UploadConfigForm: React.FC = () => {
  const restFormRef = useRef<ProFormInstance>(null);
  const [loading, setLoading] = useState(true);
  const [watermarkImages, setWatermarkImages] = useState<API.AdminUploadList[]>([]);
  const formData: API.AdminUploadConfigForm = {
    upload_storage_type: 'local',
    upload_image_max_size: 0,
    upload_image_allowed_types: [],
    upload_video_max_size: 0,
    upload_video_allowed_types: [],
    upload_document_max_size: 0,
    upload_document_allowed_types: [],
    upload_audio_max_size: 0,
    upload_audio_allowed_types: [],
    upload_compress_enabled: true,
    upload_compress_quality: 0,
    upload_compress_max_width: 0,
    upload_compress_max_height: 0,
    upload_watermark_enabled: true,
    upload_watermark_type: '',
    upload_watermark_text: '',
    upload_watermark_position: '',
    upload_watermark_opacity: '0.5',
    upload_watermark_font_size: 0,
    upload_watermark_font_color: '#FFFFFF',
    upload_watermark_font_path: '',
    upload_watermark_image_scale: '0.2',
    upload_watermark_margin: 10,
    upload_thumbnail_enabled: true,
    upload_thumbnail_width: 0,
    upload_thumbnail_height: 0,
    upload_thumbnail_quality: 0,
    upload_thumbnail_suffix: '',
  };

  return (
    <ProForm<API.AdminUploadConfigForm>
      layout="horizontal"
      labelCol={{ span: 8 }}
      wrapperCol={{ span: 10 }}
      formRef={restFormRef}
      initialValues={formData}
      onInit={async () => {
        await setLoading(true);
        const res = await edit('upload');
        if (res.code === 200) {
          restFormRef.current?.setFieldsValue(res.data);
          setWatermarkImages(res.data.upload_watermark_image_data);
        }
        await setLoading(false);
      }}
      onFinish={async (values) => {
        if (watermarkImages.length === 0 || watermarkImages[0].id < 1) {
          message.success('请输入水印图片路径');
          return;
        }
        values.upload_watermark_image = watermarkImages[0].id;
        const res = await update('upload', values);
        if (res.code === 200) {
          message.success(res.message);
        }
      }}
      submitter={{
        searchConfig: {
          submitText: '保存配置',
        },
        render: (props, defaultDoms) => {
          return (
            <div style={{ display: 'flex', justifyContent: 'center', gap: '20px' }}>
              <Button
                loading={loading}
                disabled={loading}
                key="extra-reset"
                onClick={async () => {
                  await setLoading(true);
                  const res = await edit('upload');
                  if (res.code === 200) {
                    restFormRef.current?.setFieldsValue(res.data);
                    setWatermarkImages(res.data.upload_watermark_image_data);
                  } else {
                    props.reset();
                  }
                  await setLoading(false);
                }}
              >
                重置
              </Button>
              {defaultDoms[1]}
            </div>
          );
        },
      }}
    >
      <Spin spinning={loading}>
        <ProFormRadio.Group
          name="upload_storage_type"
          label="存储类型"
          options={[
            { label: '本地存储', value: 'local' },
            { label: '阿里云OSS', value: 'aliyun_oss' },
            { label: '腾讯云COS', value: 'tencent_oss' },
            { label: '七牛云OSS', value: 'qiniu_oss' },
          ]}
          rules={[{ required: true, message: '请选择存储类型' }]}
        />
        <ProFormDigit
          name="upload_image_max_size"
          label="图片最大文件大小"
          min={1}
          max={1024}
          fieldProps={{
            precision: 0,
            suffix: 'MB',
          }}
          rules={[{ required: true, message: '请输入图片最大文件大小' }]}
        />

        <ProFormCheckbox.Group
          name="upload_image_allowed_types"
          label="允许的图片类型"
          options={[
            { label: 'jpg', value: 'jpg' },
            { label: 'jpeg', value: 'jpeg' },
            { label: 'png', value: 'png' },
            { label: 'gif', value: 'gif' },
            { label: 'bmp', value: 'bmp' },
            { label: 'webp', value: 'webp' },
          ]}
          rules={[{ required: true, message: '请选择允许的图片类型' }]}
        />

        <ProFormDigit
          name="upload_video_max_size"
          label="视频最大文件大小"
          min={1}
          max={1024}
          fieldProps={{
            precision: 0,
            suffix: 'MB',
          }}
          rules={[{ required: true, message: '请输入视频最大文件大小' }]}
        />

        <ProFormCheckbox.Group
          name="upload_video_allowed_types"
          label="允许的视频类型"
          options={[
            { label: 'mp4', value: 'mp4' },
            { label: 'avi', value: 'avi' },
            { label: 'mov', value: 'mov' },
            { label: 'wmv', value: 'wmv' },
            { label: 'flv', value: 'flv' },
            { label: 'mkv', value: 'mkv' },
          ]}
          rules={[{ required: true, message: '请选择允许的视频类型' }]}
        />

        <ProFormDigit
          name="upload_document_max_size"
          label="文档最大文件大小"
          min={1}
          max={1024}
          fieldProps={{
            precision: 0,
            suffix: 'MB',
          }}
          rules={[{ required: true, message: '请输入文档最大文件大小' }]}
        />

        <ProFormCheckbox.Group
          name="upload_document_allowed_types"
          label="允许的文档类型"
          options={[
            { label: 'pdf', value: 'pdf' },
            { label: 'doc', value: 'doc' },
            { label: 'docx', value: 'docx' },
            { label: 'xls', value: 'xls' },
            { label: 'xlsx', value: 'xlsx' },
            { label: 'ppt', value: 'ppt' },
            { label: 'pptx', value: 'pptx' },
            { label: 'txt', value: 'txt' },
          ]}
          rules={[{ required: true, message: '请选择允许的文档类型' }]}
        />

        <ProFormDigit
          name="upload_audio_max_size"
          label="音频最大文件大小"
          min={1}
          max={1024}
          fieldProps={{
            precision: 0,
            suffix: 'MB',
          }}
          rules={[{ required: true, message: '请输入音频最大文件大小' }]}
        />

        <ProFormCheckbox.Group
          name="upload_audio_allowed_types"
          label="允许的音频类型"
          options={[
            { label: 'mp3', value: 'mp3' },
            { label: 'wav', value: 'wav' },
            { label: 'aac', value: 'aac' },
            { label: 'flac', value: 'flac' },
            { label: 'ogg', value: 'ogg' },
            { label: 'm4a', value: 'm4a' },
          ]}
          rules={[{ required: true, message: '请选择允许的音频类型' }]}
        />

        <ProFormSwitch
          name="upload_compress_enabled"
          label="是否启用图片压缩"
          fieldProps={{
            checkedChildren: '是',
            unCheckedChildren: '否',
          }}
        />

        <ProFormDigit
          name="upload_compress_quality"
          label="图片压缩质量"
          min={1}
          max={100}
          fieldProps={{
            precision: 0,
          }}
          rules={[{ required: true, message: '请输入图片压缩质量' }]}
        />

        <ProFormDigit
          name="upload_compress_max_width"
          label="图片最大宽度"
          min={1}
          fieldProps={{
            precision: 0,
            suffix: 'px',
          }}
          rules={[{ required: true, message: '请输入图片最大宽度' }]}
        />

        <ProFormDigit
          name="upload_compress_max_height"
          label="图片最大高度"
          min={1}
          fieldProps={{
            precision: 0,
            suffix: 'px',
          }}
          rules={[{ required: true, message: '请输入图片最大高度' }]}
        />

        <ProFormSwitch
          name="upload_watermark_enabled"
          label="是否启用水印"
          fieldProps={{
            checkedChildren: '是',
            unCheckedChildren: '否',
          }}
        />

        <ProFormSelect
          name="upload_watermark_type"
          label="水印类型"
          options={[
            { label: '文字水印', value: 'text' },
            { label: '图片水印', value: 'image' },
          ]}
          rules={[{ required: true, message: '请选择水印类型' }]}
        />

        <ProFormText
          name="upload_watermark_text"
          label="水印文字"
          placeholder="请输入水印文字"
          fieldProps={{
            maxLength: 100,
            showCount: true,
          }}
        />

        <ProFormSelect
          name="upload_watermark_position"
          label="水印位置"
          options={[
            { label: '左上角', value: 'top-left' },
            { label: '右上角', value: 'top-right' },
            { label: '左下角', value: 'bottom-left' },
            { label: '右下角', value: 'bottom-right' },
            { label: '居中', value: 'center' },
          ]}
          rules={[{ required: true, message: '请选择水印位置' }]}
        />

        <ProFormText
          name="upload_watermark_opacity"
          label="水印透明度"
          placeholder="请输入水印透明度(0-1)"
          fieldProps={{
            maxLength: 10,
          }}
          rules={[
            { required: true, message: '请输入水印透明度' },
            {
              pattern: /^(0(\.\d+)?|1(\.0+)?)$/,
              message: '请输入0-1之间的数字',
            },
          ]}
        />

        <ProFormDigit
          name="upload_watermark_font_size"
          label="水印字体大小"
          min={1}
          fieldProps={{
            precision: 0,
            suffix: 'px',
          }}
          rules={[{ required: true, message: '请输入水印字体大小' }]}
        />
        <Form.Item
          label="水印字体颜色"
          name="upload_watermark_font_color"
          rules={[{ required: true, message: '请选择水印字体颜色' }]}
        >
          <ColorPicker showText disabledAlpha />
        </Form.Item>
        <ProFormSelect
          name="upload_watermark_font_path"
          label="水印字体文件路径"
          placeholder="请选择水印字体"
          options={[
            {
              label: '思源黑体 SC 中文覆盖最全 中文 + 英文 + 符号一致性好 视频标题 图片 / 视频水印',
              value: 'assets/fonts/SourceHanSansSC-Regular.otf',
            },
            {
              label:
                '思源宋体 SC 中文有衬线（宋体）阅读体验好 长文本不累眼 中文标点、段落表现优秀 视频字幕 图片正文',
              value: 'assets/fonts/SourceHanSerifSC-Regular.otf',
            },
            {
              label: '阿里巴巴普惠体 中文无衬线 线条清晰，现代感强 非常适合短视频、小屏幕',
              value: 'assets/fonts/AlibabaPuHuiTi-3-55-Regular.ttf',
            },
            {
              label: 'Google 英文无衬线 英文水印 数字、时间戳 中英文混排（英文部分）',
              value: 'assets/fonts/Roboto-Regular.ttf',
            },
            {
              label: 'Google 英文无衬线 英文字幕 英文说明文字 图片正文',
              value: 'assets/fonts/OpenSans-Regular.ttf',
            },
          ]}
          fieldProps={{
            showSearch: true,
          }}
        />

        <Form.Item label="水印图片">
          <ImageUpload
            value={watermarkImages}
            onChange={(files) => {
              if (!files) {
                // 删除情况：files 是 undefined 或 null
                setWatermarkImages([]);
              } else if (Array.isArray(files)) {
                // 多选情况：files 是数组
                setWatermarkImages(files);
              } else {
                // 单选情况：files 是单个对象
                setWatermarkImages([files]);
              }
            }}
          />
        </Form.Item>

        <ProFormText
          name="upload_watermark_image_scale"
          label="水印图片缩放比例"
          placeholder="请输入水印图片缩放比例(0-1)"
          fieldProps={{
            maxLength: 10,
          }}
          rules={[
            {
              pattern: /^(0(\.\d+)?|1(\.0+)?)$/,
              message: '请输入0-1之间的数字',
            },
          ]}
        />

        <ProFormDigit
          name="upload_watermark_margin"
          label="水印边距"
          min={0}
          fieldProps={{
            precision: 0,
            suffix: 'px',
          }}
          rules={[{ required: true, message: '请输入水印边距' }]}
        />

        <ProFormSwitch
          name="upload_thumbnail_enabled"
          label="是否生成缩略图"
          fieldProps={{
            checkedChildren: '是',
            unCheckedChildren: '否',
          }}
        />

        <ProFormDigit
          name="upload_thumbnail_width"
          label="缩略图宽度"
          min={1}
          fieldProps={{
            precision: 0,
            suffix: 'px',
          }}
          rules={[{ required: true, message: '请输入缩略图宽度' }]}
        />

        <ProFormDigit
          name="upload_thumbnail_height"
          label="缩略图高度"
          min={1}
          fieldProps={{
            precision: 0,
            suffix: 'px',
          }}
          rules={[{ required: true, message: '请输入缩略图高度' }]}
        />

        <ProFormDigit
          name="upload_thumbnail_quality"
          label="缩略图质量"
          min={1}
          max={100}
          fieldProps={{
            precision: 0,
          }}
          rules={[{ required: true, message: '请输入缩略图质量' }]}
        />

        <ProFormText
          name="upload_thumbnail_suffix"
          label="缩略图文件名后缀"
          placeholder="请输入缩略图文件名后缀"
          fieldProps={{
            maxLength: 50,
            showCount: true,
          }}
          rules={[{ required: true, message: '请输入缩略图文件名后缀' }]}
        />
      </Spin>
    </ProForm>
  );
};

export default UploadConfigForm;
