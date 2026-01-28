import { Footer } from '@/components';
import { generateCaptcha, login, saveTokens } from '@/services/admin/common/api';
import { CodeOutlined, LockOutlined, UserOutlined } from '@ant-design/icons';
import { LoginForm, ProFormText } from '@ant-design/pro-components';
import { Helmet, useModel } from '@umijs/max';
import { Image, message } from 'antd';
import React, { useEffect, useState } from 'react';
import Settings from '../../../config/defaultSettings';
const Login: React.FC = () => {
  const [captchaData, setCaptchaData] = useState<{
    captcha_id: string;
    captcha_image: string;
  } | null>(null);
  const { initialState } = useModel('@@initialState');
  const { systemConfig } = initialState || {};

  // 获取验证码
  const fetchCaptcha = async () => {
    const res = await generateCaptcha();
    if (res.code === 200) {
      setCaptchaData({
        captcha_id: res.data.captcha_id,
        captcha_image: res.data.image_data,
      });
    }
  };
  // 页面加载时获取验证码和系统配置
  useEffect(() => {
    fetchCaptcha();
  }, []);

  const handleSubmit = async (values: any) => {
    // 登录
    const res = await login({
      username: values.username as string,
      password: values.password as string,
      captcha: values.captcha,
      captcha_id: captchaData?.captcha_id,
    });
    if (res.code === 200) {
      saveTokens(res.data);
      message.success('登录成功！');
      const urlParams = new URL(window.location.href).searchParams;
      window.location.href = urlParams.get('redirect') || '/';
      return;
    }
    // 登录失败后重新获取验证码
    fetchCaptcha();
  };

  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        height: '100vh',
        overflow: 'auto',
      }}
    >
      <Helmet>
        <title>{`登录页${systemConfig?.site_name ? ` - ${systemConfig.site_name}` : ''}`}</title>
        {systemConfig?.site_description && (
          <meta name="description" content={systemConfig.site_description} />
        )}
        {systemConfig?.site_keywords && (
          <meta name="keywords" content={systemConfig.site_keywords} />
        )}
      </Helmet>
      <div
        style={{
          flex: '1',
          padding: '32px 0',
        }}
      >
        <LoginForm
          contentStyle={{
            minWidth: 280,
            maxWidth: '75vw',
          }}
          logo={<img alt="logo" src={systemConfig?.site_logo_data?.[0]?.url || '/logo.svg'} />}
          title={systemConfig?.site_name || Settings.title}
          subTitle={systemConfig?.site_description || Settings.title}
          onFinish={async (values) => {
            await handleSubmit(values as API.AdminLoginParams);
          }}
        >
          <div>
            <ProFormText
              name="username"
              fieldProps={{
                size: 'large',
                prefix: <UserOutlined />,
                autoFocus: true,
                autoComplete: 'username',
              }}
              placeholder="请输入用户名"
              rules={[
                {
                  required: true,
                  message: '请输入用户名!',
                },
              ]}
            />
            <ProFormText.Password
              name="password"
              fieldProps={{
                size: 'large',
                prefix: <LockOutlined />,
                autoComplete: 'current-password',
              }}
              placeholder="请输入密码"
              rules={[
                {
                  required: true,
                  message: '请输入密码！',
                },
              ]}
            />

            {/* 验证码输入框 */}
            <div
              style={{
                display: 'flex',
                gap: '8px',
                alignItems: 'flex-start',
                marginBottom: '24px',
              }}
            >
              <ProFormText
                name="captcha"
                fieldProps={{
                  size: 'large',
                  prefix: <CodeOutlined />,
                  placeholder: '请输入验证码',
                  style: { flex: 1 },
                }}
                rules={[
                  {
                    required: true,
                    message: '请输入验证码！',
                  },
                ]}
              />
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <div style={{ position: 'relative' }}>
                  {captchaData && (
                    <Image
                      src={captchaData.captcha_image}
                      alt="验证码"
                      preview={false}
                      style={{
                        height: '40px',
                        border: '1px solid #d9d9d9',
                        borderRadius: '6px',
                        cursor: 'pointer', // 添加指针样式
                      }}
                      onClick={fetchCaptcha} // 点击图片刷新验证码
                    />
                  )}
                </div>
              </div>
            </div>
          </div>
        </LoginForm>
      </div>
      <Footer copyright={systemConfig?.copyright} />
    </div>
  );
};

export default Login;
