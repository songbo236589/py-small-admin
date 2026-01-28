import { SettingOutlined } from '@ant-design/icons';
import { Button, Popconfirm } from 'antd';
import React from 'react';
interface TypeProps {
  onCancel?: any;
  visible?: boolean;
  confirmLoading?: boolean;
  title?: string;
  disabled?: boolean;
}
class ResetPwd extends React.Component<any, TypeProps> {
  constructor(props: TypeProps) {
    super(props);
    this.state = {
      visible: false,
      confirmLoading: false,
      ...props,
    };
  }
  static defaultProps: TypeProps = {
    title: '您确定要初始化密码吗？',
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
      <>
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
            onClick={() => {
              this.showPopconfirm();
            }}
          >
            <SettingOutlined />
            初始化密码
          </Button>
        </Popconfirm>
      </>
    );
  }
}
export default ResetPwd;
