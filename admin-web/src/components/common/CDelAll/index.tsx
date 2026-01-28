import { Popconfirm } from 'antd';
import React from 'react';
interface TypeProps {
  onCancel?: any;
  visible?: boolean;
  confirmLoading?: boolean;
  title?: string;
  disabled?: boolean;
  count: number;
}
class CDelAll extends React.Component<any, TypeProps> {
  constructor(props: TypeProps) {
    super(props);
    this.state = {
      visible: false,
      confirmLoading: false,
      ...props,
    };
  }
  handleOk = async () => {
    this.setState({ confirmLoading: true });
    await this.state.onCancel();
    this.setState({ confirmLoading: false, visible: false });
  };

  handleCancel = () => {
    this.setState({ visible: false });
  };
  showPopconfirm = () => {
    this.setState({ visible: true });
  };
  render() {
    return (
      <div>
        <Popconfirm
          title={this.state.title || `您确定要删除选中的${this.state.count}项数据吗？`}
          open={this.state.visible}
          onConfirm={this.handleOk}
          okButtonProps={{ loading: this.state.confirmLoading }}
          onCancel={this.handleCancel}
        >
          <a
            onClick={() => {
              this.showPopconfirm();
            }}
          >
            批量删除
          </a>
        </Popconfirm>
      </div>
    );
  }
}
export default CDelAll;
