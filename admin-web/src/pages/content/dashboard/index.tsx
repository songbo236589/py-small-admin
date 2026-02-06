import { useModel } from '@umijs/max';
import { Card, theme, Row, Col, Statistic } from 'antd';
import React from 'react';
import {
  FileTextOutlined,
  FolderOutlined,
  TagsOutlined,
  UserSwitchOutlined,
  SendOutlined,
  EyeOutlined,
} from '@ant-design/icons';

/**
 * 内容统计卡片
 */
const ContentCard: React.FC<{
  title: string;
  count: number;
  icon: React.ReactNode;
  color: string;
  description: string;
  link: string;
}> = ({ title, count, icon, color, description, link }) => {
  const { useToken } = theme;
  const { token } = useToken();

  return (
    <a
      href={link}
      style={{ textDecoration: 'none' }}
      target={link.startsWith('http') ? '_blank' : '_self'}
    >
      <div
        style={{
          backgroundColor: token.colorBgContainer,
          boxShadow: token.boxShadow,
          borderRadius: '8px',
          padding: '20px',
          height: '100%',
          transition: 'all 0.3s',
          border: '1px solid transparent',
        }}
        onMouseEnter={(e) => {
          e.currentTarget.style.borderColor = color;
          e.currentTarget.style.transform = 'translateY(-4px)';
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.borderColor = 'transparent';
          e.currentTarget.style.transform = 'translateY(0)';
        }}
      >
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            marginBottom: '12px',
          }}
        >
          <div
            style={{
              width: '48px',
              height: '48px',
              borderRadius: '50%',
              backgroundColor: color,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              marginRight: '16px',
              fontSize: '24px',
              color: '#fff',
            }}
          >
            {icon}
          </div>
          <div style={{ flex: 1 }}>
            <div
              style={{
                fontSize: '16px',
                fontWeight: 500,
                color: token.colorText,
                marginBottom: '4px',
              }}
            >
              {title}
            </div>
            <div
              style={{
                fontSize: '12px',
                color: token.colorTextSecondary,
              }}
            >
              {description}
            </div>
          </div>
        </div>
        <div
          style={{
            fontSize: '32px',
            fontWeight: 600,
            color: color,
          }}
        >
          {count}
        </div>
      </div>
    </a>
  );
};

const Index: React.FC = () => {
  const { token } = theme.useToken();
  const { initialState } = useModel('@@initialState');

  return (
    <Card
      style={{ borderRadius: 8 }}
      styles={{
        body: {
            backgroundImage:
              initialState?.settings?.navTheme === 'realDark'
                ? 'background-image: linear-gradient(75deg, #1A1B1F 0%, #191C1F 100%)'
                : 'background-image: linear-gradient(75deg, #FBFDFF 0%, #F5F7FF 100%)',
        },
      }}
    >
      <div
        style={{
          backgroundPosition: '100% -30%',
          backgroundRepeat: 'no-repeat',
          backgroundSize: '274px auto',
          backgroundImage:
            "url('https://gw.alipayobjects.com/mdn/rms_a9745b/afts/img/A*BuFmQqsB2iAAAAAAAAAAAAAAARQnAQ')",
        }}
      >
        <div
          style={{
            fontSize: '20px',
            color: token.colorTextHeading,
          }}
        >
          欢迎使用内容管理系统
        </div>
        <p
          style={{
            fontSize: '14px',
            color: token.colorTextSecondary,
            lineHeight: '22px',
            marginTop: 16,
            marginBottom: 32,
            width: '65%',
          }}
        >
          这是一个功能完善的内容管理模块，支持文章创作、多平台发布等功能。
        </p>

        {/* 内容统计卡片 */}
        <Row gutter={[16, 16]} style={{ marginBottom: 32 }}>
          <Col xs={24} sm={12} md={8} lg={6}>
            <ContentCard
              title="文章总数"
              count={128}
              icon={<FileTextOutlined />}
              color="#1677FF"
              description="已发布文章"
              link="/content/manage/article"
            />
          </Col>
          <Col xs={24} sm={12} md={8} lg={6}>
            <ContentCard
              title="分类数量"
              count={12}
              icon={<FolderOutlined />}
              color="#52C41A"
              description="内容分类"
              link="/content/manage/category"
            />
          </Col>
          <Col xs={24} sm={12} md={8} lg={6}>
            <ContentCard
              title="标签数量"
              count={36}
              icon={<TagsOutlined />}
              color="#FA8C16"
              description="文章标签"
              link="/content/manage/tag"
            />
          </Col>
          <Col xs={24} sm={12} md={8} lg={6}>
            <ContentCard
              title="平台账号"
              count={5}
              icon={<UserSwitchOutlined />}
              color="#13C2C2"
              description="已绑定账号"
              link="/content/manage/platform_account"
            />
          </Col>
        </Row>

        {/* 快速统计 */}
        <Row gutter={[16, 16]}>
          <Col xs={24} sm={12} md={8}>
            <Card
              title="发布统计"
              bordered={false}
              style={{ height: '100%' }}
            >
              <Row gutter={[16, 16]}>
                <Col span={8}>
                  <Statistic
                    title="今日发布"
                    value={3}
                    valueStyle={{ color: '#3f8600' }}
                    prefix={<SendOutlined />}
                  />
                </Col>
                <Col span={8}>
                  <Statistic
                    title="待发布"
                    value={8}
                    valueStyle={{ color: '#cf1322' }}
                  />
                </Col>
                <Col span={8}>
                  <Statistic
                    title="总发布量"
                    value={156}
                    suffix="篇"
                  />
                </Col>
              </Row>
            </Card>
          </Col>
          <Col xs={24} sm={12} md={8}>
            <Card
              title="浏览统计"
              bordered={false}
              style={{ height: '100%' }}
            >
              <Row gutter={[16, 16]}>
                <Col span={8}>
                  <Statistic
                    title="今日浏览"
                    value={1234}
                    prefix={<EyeOutlined />}
                  />
                </Col>
                <Col span={8}>
                  <Statistic
                    title="本周浏览"
                    value={8625}
                  />
                </Col>
                <Col span={8}>
                  <Statistic
                    title="总浏览量"
                    value={45678}
                  />
                </Col>
              </Row>
            </Card>
          </Col>
          <Col xs={24} sm={12} md={8}>
            <Card
              title="快捷操作"
              bordered={false}
              style={{ height: '100%' }}
            >
              <div
                style={{
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '12px',
                }}
              >
                <a href="/content/manage/article" style={{ fontSize: '14px' }}>
                  <FileTextOutlined /> 新建文章
                </a>
                <a href="/content/manage/category" style={{ fontSize: '14px' }}>
                  <FolderOutlined /> 管理分类
                </a>
                <a href="/content/manage/publish" style={{ fontSize: '14px' }}>
                  <SendOutlined /> 发布管理
                </a>
              </div>
            </Card>
          </Col>
        </Row>
      </div>
    </Card>
  );
};

export default Index;
