import { Card, Tabs } from 'antd';
import React from 'react';
import EmailConfigForm from './components/EmailConfigForm';
import SysConfigForm from './components/SysConfigForm';
import UploadConfigForm from './components/UploadConfigForm';

const Index: React.FC = () => {
  return (
    <Card>
      <Tabs
        type="card"
        items={[
          {
            label: '系统基础配置',
            key: '1',
            children: (
              <div style={{ padding: '24px' }}>
                <SysConfigForm />
              </div>
            ),
          },
          {
            label: '文件上传配置',
            key: '2',
            children: (
              <div style={{ padding: '24px' }}>
                <UploadConfigForm />
              </div>
            ),
          },
          {
            label: '邮件配置',
            key: '3',
            children: (
              <div style={{ padding: '24px' }}>
                <EmailConfigForm />
              </div>
            ),
          },
        ]}
      />
    </Card>
  );
};

export default Index;
