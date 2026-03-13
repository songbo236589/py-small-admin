import { useModel } from '@umijs/max';
import { Card, message, theme, Row, Col, Statistic, Spin } from 'antd';
import React, { useEffect, useState } from 'react';
import {
  FileTextOutlined,
  FolderOutlined,
  TagsOutlined,
  UserSwitchOutlined,
  SendOutlined,
} from '@ant-design/icons';
import { getStatistics } from '@/services/content/dashboard/api';

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

  const isExternalLink = link.startsWith('http');
  return (
    <a
      href={link}
      style={{ textDecoration: 'none' }}
      target={isExternalLink ? '_blank' : '_self'}
      rel={isExternalLink ? 'noreferrer' : undefined}
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
  const [loading, setLoading] = useState(true);
  const [statistics, setStatistics] = useState<API.ContentDashboardStatistics | null>(null);

  // 获取统计数据
  useEffect(() => {
    const fetchStatistics = async () => {
      try {
        const response = await getStatistics();
        if (response.data) {
          setStatistics(response.data);
        }
      } catch (error) {
        message.error('获取统计数据失败');
      } finally {
        setLoading(false);
      }
    };
    fetchStatistics();
  }, []);

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
        <Spin spinning={loading}>
          <Row gutter={[16, 16]} style={{ marginBottom: 32 }}>
            <Col xs={24} sm={12} md={8} lg={6}>
              <ContentCard
                title="文章总数"
                count={statistics?.article_count ?? 0}
                icon={<FileTextOutlined />}
                color="#1677FF"
                description="已发布文章"
                link="/content/manage/article"
              />
            </Col>
            <Col xs={24} sm={12} md={8} lg={6}>
              <ContentCard
                title="分类数量"
                count={statistics?.category_count ?? 0}
                icon={<FolderOutlined />}
                color="#52C41A"
                description="内容分类"
                link="/content/manage/category"
              />
            </Col>
            <Col xs={24} sm={12} md={8} lg={6}>
              <ContentCard
                title="标签数量"
                count={statistics?.tag_count ?? 0}
                icon={<TagsOutlined />}
                color="#FA8C16"
                description="文章标签"
                link="/content/manage/tag"
              />
            </Col>
            <Col xs={24} sm={12} md={8} lg={6}>
              <ContentCard
                title="平台账号"
                count={statistics?.platform_account_count ?? 0}
                icon={<UserSwitchOutlined />}
                color="#13C2C2"
                description="已绑定账号"
                link="/content/manage/platform_account"
              />
            </Col>
          </Row>
        </Spin>

        {/* 快速统计 */}
        <Spin spinning={loading}>
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
                      value={statistics?.publish?.today ?? 0}
                      valueStyle={{ color: '#3f8600' }}
                      prefix={<SendOutlined />}
                    />
                  </Col>
                  <Col span={8}>
                    <Statistic
                      title="待发布"
                      value={statistics?.publish?.pending ?? 0}
                      valueStyle={{ color: '#cf1322' }}
                    />
                  </Col>
                  <Col span={8}>
                    <Statistic
                      title="总发布量"
                      value={statistics?.publish?.total ?? 0}
                      suffix="篇"
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
        </Spin>
      </div>
    </Card>
  );
};

export default Index;
