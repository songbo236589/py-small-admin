import { DefaultFooter } from '@ant-design/pro-components';
import React from 'react';

interface FooterProps {
  copyright?: string;
}

const Footer: React.FC<FooterProps> = ({ copyright }) => {
  const defaultMessage = '天奇扬网络技术有限公司出品';

  const currentYear = new Date().getFullYear();
  return (
    <DefaultFooter
      style={{
        backgroundColor: 'none',
      }}
      copyright={`${copyright || currentYear + defaultMessage}`}
      // links={[
      //   {
      //     key: 'Ant Design Pro',
      //     title: 'Ant Design Pro',
      //     href: 'https://pro.ant.design',
      //     blankTarget: true,
      //   },
      //   {
      //     key: 'github',
      //     title: <GithubOutlined />,
      //     href: 'https://github.com/ant-design/ant-design-pro',
      //     blankTarget: true,
      //   },
      //   {
      //     key: 'Ant Design',
      //     title: 'Ant Design',
      //     href: 'https://ant.design',
      //     blankTarget: true,
      //   },
      // ]}
    />
  );
};

export default Footer;
