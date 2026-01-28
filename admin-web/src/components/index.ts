/**
 * 这个文件作为组件的目录
 * 目的是统一管理对外输出的组件，方便分类
 */
/**
 * 布局组件
 */
import Footer from './Footer';
import { Question } from './RightContent';
import { AvatarDropdown, AvatarName } from './RightContent/AvatarDropdown';
import CDel from './common/CDel';
import CDelAll from './common/CDelAll';
import NumberInput from './common/NumberInput';
import ProFormTinyMCE from './common/ProFormTinyMCE';
import ProTableWrapper from './common/ProTableWrapper';
/**
 * 上传组件
 */
export {
  AudiosUpload,
  DocumentUpload,
  ImageUpload,
  MediaLibraryModal,
  VideoUpload,
} from './common/Upload';

export {
  AvatarDropdown,
  AvatarName,
  CDel,
  CDelAll,
  Footer,
  NumberInput,
  ProFormTinyMCE,
  ProTableWrapper,
  Question,
};
