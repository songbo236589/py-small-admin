import type { ProTableProps } from '@ant-design/pro-components';
import { ProTable } from '@ant-design/pro-components';
import { Space } from 'antd';

/**
 * 默认分页配置
 */
const DEFAULT_PAGINATION = {
  showSizeChanger: true,
  pageSizeOptions: ['10', '20', '50', '100', '500'],
  showQuickJumper: true,
  showTotal: (total: number) => `共 ${total} 条数据`,
  size: 'middle',
  disabled: false,
};

/**
 * ProTable 包装组件
 * 封装全局默认分页配置
 */
const ProTableWrapper = <
  T extends Record<string, any>,
  U extends Record<string, any> = Record<string, any>,
>(
  props: ProTableProps<T, U>,
) => {
  const { pagination, ...restProps } = props;

  return (
    <ProTable
      scroll={{ x: 1300, y: 'calc(100vh - 400px)' }}
      pagination={{
        ...DEFAULT_PAGINATION,
        ...pagination,
      }}
      options={{
        fullScreen: true,
        setting: {
          listsHeight: 400,
        },
      }}
      tableAlertRender={({ selectedRowKeys, onCleanSelected }) => (
        <Space size={24}>
          <span>
            已选 {selectedRowKeys.length} 项
            <a style={{ marginLeft: 8 }} onClick={onCleanSelected}>
              取消选择
            </a>
          </span>
        </Space>
      )}
      {...(restProps as any)}
    />
  );
};

export default ProTableWrapper;
