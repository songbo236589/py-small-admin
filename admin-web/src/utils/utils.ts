const getSort = async (params: API.ListQequest, sort: any) => {
  const paramsData = JSON.parse(JSON.stringify(params));
  if (JSON.stringify(sort) !== '{}') {
    const sortData = JSON.parse(JSON.stringify(sort));
    for (const x in sortData) {
      if (sortData[x] === 'ascend') {
        sortData[x] = 'desc';
      } else {
        sortData[x] = 'asc';
      }
    }
    paramsData.sort = sortData;
  }
  if (paramsData.current) {
    paramsData.page = paramsData.current;
    delete paramsData.current;
  }
  if (paramsData.pageSize) {
    paramsData.limit = paramsData.pageSize;
    delete paramsData.pageSize;
  }
  return paramsData;
};

const setLsetData = async (res: API.ResponseData) => {
  if (res.code === 200) {
    return {
      success: true,
      data: res.data.items,
      total: res.data.total,
    };
  }
  return {};
};
export { getSort, setLsetData };
