import { history, useModel } from '@umijs/max';
import { Button, Card, Result } from 'antd';
import React from 'react';

const NoFoundPage: React.FC = () => {
  const { initialState } = useModel('@@initialState');
  const siteName = initialState?.systemConfig?.site_name || '系统';

  return (
    <Card variant="borderless">
      <Result
        status="404"
        title="404"
        subTitle={`抱歉，您访问的${siteName}页面不存在。`}
        extra={
          <Button type="primary" onClick={() => history.push('/')}>
            返回首页
          </Button>
        }
      />
    </Card>
  );
};

export default NoFoundPage;
