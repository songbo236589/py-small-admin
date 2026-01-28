import { Input } from 'antd';
import type { FocusEventHandler } from 'react';
import React from 'react';
interface TypeSort {
  key?: number;
  value: string;
  placeholder: string;
  onBlur: FocusEventHandler | undefined;
  maxLength?: number;
}
class NumberInput extends React.Component<any, TypeSort> {
  constructor(props: TypeSort) {
    super(props);
    this.state = { ...props };
  }
  static defaultProps: TypeSort = {
    value: '',
    placeholder: '请输入排序',
    onBlur: undefined,
    maxLength: 11,
  };
  onChange = (e: { target: { value: any } }) => {
    const { value } = e.target;
    const reg = /^[1-9]\d*$/;
    if ((!isNaN(value) && reg.test(value)) || value === '') {
      this.setState({ value });
    }
  };
  onBlur = () => {
    this.props.onBlur(parseInt(this.state.value));
  };
  render() {
    return <Input {...this.state} onChange={this.onChange} onBlur={this.onBlur} />;
  }
}
export default NumberInput;
