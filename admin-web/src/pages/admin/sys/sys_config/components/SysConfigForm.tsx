import { ImageUpload, ProFormTinyMCE } from '@/components';
import { edit, update } from '@/services/admin/sys/sys_config/api';
import type { ProFormInstance } from '@ant-design/pro-components';
import { ProForm, ProFormText, ProFormTextArea } from '@ant-design/pro-components';
import { Button, Form, message, Spin } from 'antd';
import React, { useRef, useState } from 'react';
const SysConfigForm: React.FC = () => {
  const restFormRef = useRef<ProFormInstance>(null);
  const [loading, setLoading] = useState(true);
  const [logoImages, setLogoImages] = useState<API.AdminUploadList[]>([]);
  const [faviconImages, setFaviconImages] = useState<API.AdminUploadList[]>([]);
  const formData: API.AdminSysConfigForm = {
    site_name: '',
    site_description: '',
    site_keywords: '',
    copyright: '',
    site_content: '',
  };

  return (
    <ProForm<API.AdminSysConfigForm>
      layout="horizontal"
      labelCol={{ span: 8 }}
      wrapperCol={{ span: 10 }}
      formRef={restFormRef}
      initialValues={formData}
      onInit={async () => {
        await setLoading(true);
        const res = await edit('system');
        if (res.code === 200) {
          restFormRef.current?.setFieldsValue(res.data);
          setLogoImages(res.data.site_logo_data);
          setFaviconImages(res.data.site_favicon_data);
        }
        await setLoading(false);
      }}
      onFinish={async (values) => {
        if (logoImages.length === 0 || logoImages[0].id < 1) {
          message.success('请上传网站Logo');
          return;
        }

        if (faviconImages.length === 0 || faviconImages[0].id < 1) {
          message.success('请上传网站图标');
          return;
        }

        values.site_logo = logoImages[0].id;
        values.site_favicon = faviconImages[0].id;
        const res = await update('system', values);
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
                  const res = await edit('system');
                  if (res.code === 200) {
                    restFormRef.current?.setFieldsValue(res.data);
                    setLogoImages(res.data.site_logo_data);
                    setFaviconImages(res.data.site_favicon_data);
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
        <ProFormText
          name="site_name"
          label="网站名称"
          placeholder="请输入网站名称"
          fieldProps={{
            maxLength: 100,
            showCount: true,
          }}
          rules={[{ required: true, message: '请输入网站名称' }]}
        />

        <ProFormTextArea
          name="site_description"
          label="网站描述"
          placeholder="请输入网站描述"
          fieldProps={{
            maxLength: 500,
            rows: 4,
            showCount: true,
          }}
        />

        <ProFormText
          name="site_keywords"
          label="网站关键词"
          placeholder="请输入网站关键词，多个关键词用逗号分隔"
          fieldProps={{
            maxLength: 500,
            showCount: true,
          }}
        />
        <Form.Item label="网站Logo">
          <ImageUpload
            value={logoImages}
            onChange={(files) => {
              if (!files) {
                // 删除情况：files 是 undefined 或 null
                setLogoImages([]);
              } else if (Array.isArray(files)) {
                // 多选情况：files 是数组
                setLogoImages(files);
              } else {
                // 单选情况：files 是单个对象
                setLogoImages([files]);
              }
            }}
          />
        </Form.Item>
        <Form.Item label="网站图标">
          <ImageUpload
            value={faviconImages}
            onChange={(files) => {
              if (!files) {
                // 删除情况：files 是 undefined 或 null
                setFaviconImages([]);
              } else if (Array.isArray(files)) {
                // 多选情况：files 是数组
                setFaviconImages(files);
              } else {
                // 单选情况：files 是单个对象
                setFaviconImages([files]);
              }
            }}
          />
        </Form.Item>

        <ProFormTinyMCE
          name="site_content"
          label="关于我们"
          placeholder="请输入关于我们..."
          formRef={restFormRef}
          height={500}
        />

        <ProFormText
          name="copyright"
          label="版权信息"
          placeholder="请输入版权信息"
          fieldProps={{
            maxLength: 200,
            showCount: true,
          }}
        />
      </Spin>
    </ProForm>
  );
};

export default SysConfigForm;
