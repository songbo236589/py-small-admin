import type { ProColumns } from '@ant-design/pro-components';
import * as XLSX from 'xlsx';

interface ExportExcelParams {
  breadcrumbData: any[];
  columns: ProColumns<any>[];
  columnsState: Record<string, any>;
  selectedRows: any[];
}

export function exportExcel({
  breadcrumbData,
  columns,
  columnsState,
  selectedRows,
}: ExportExcelParams) {
  if (!selectedRows || selectedRows.length === 0) {
    return;
  }
  /**
   * 1. 过滤 & 排序列
   * - 忽略操作列
   * - 只导出显示的列
   * - 按当前列顺序排序
   */
  const exportColumns = columns
    .filter((col) => {
      if (!col.dataIndex) return false;
      if (col.hideInTable) return false;

      const state = columnsState?.[col.dataIndex as string];
      return state?.show !== false;
    })
    .sort((a, b) => {
      const orderA = columnsState?.[a.dataIndex as string]?.order ?? 0;
      const orderB = columnsState?.[b.dataIndex as string]?.order ?? 0;
      return orderA - orderB;
    });
  /**
   * 2. 构建导出数据
   * - key 用列 title（Excel 表头）
   * - value 处理 valueEnum / renderText
   */
  const exportData = selectedRows.map((row) => {
    const obj: Record<string, any> = {};

    exportColumns.forEach((col) => {
      obj[String(col.title)] = row[col.dataIndex as string];
    });
    console.log(obj);
    return obj;
  });
  // console.log(exportData);
  /**
   * 3. 生成 Excel
   */
  const worksheet = XLSX.utils.json_to_sheet(exportData);
  const workbook = XLSX.utils.book_new();

  XLSX.utils.book_append_sheet(workbook, worksheet, '数据');
  let fileName = '数据';
  if (breadcrumbData.length > 0) {
    fileName = breadcrumbData[breadcrumbData.length - 1].title;
  }
  XLSX.writeFile(workbook, `${fileName}.xlsx`);
}
