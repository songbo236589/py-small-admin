import { DeleteOutlined } from '@ant-design/icons';
import { Button, Popconfirm } from 'antd';
import React from 'react';
interface TypeProps {
  onCancel?: any;
  visible?: boolean;
  confirmLoading?: boolean;
  title?: string;
  disabled?: boolean;
}
class CDel extends React.Component<any, TypeProps> {
  constructor(props: TypeProps) {
    super(props);
    this.state = {
      visible: false,
      confirmLoading: false,
      ...props,
    };
  }
  static defaultProps: TypeProps = {
    title: '您确定要删除该项数据吗？',
  };
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
          title={this.state.title}
          open={this.state.visible}
          onConfirm={this.handleOk}
          okButtonProps={{ loading: this.state.confirmLoading }}
          onCancel={this.handleCancel}
        >
          <Button
            type="primary"
            size="small"
            disabled={this.state.disabled ? true : false}
            danger
            onClick={() => {
              this.showPopconfirm();
            }}
          >
            <DeleteOutlined />
            删除
          </Button>
        </Popconfirm>
      </div>
    );
  }
}
export default CDel;
