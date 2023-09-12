async function getQueryParamValue(name) {
  const searchParams = new URLSearchParams(window.location.search);
  const value = searchParams.get(name);
  return value !== null ? value : window.location.href;
}

async function getDomain(range='none'){
  const url = decodeURIComponent(await getQueryParamValue("src"));
  const baseUrl = url.substring(0, url.lastIndexOf('?') != -1 ? url.lastIndexOf('?') : url.length).replace(/\/p\//, '/');
  let DOMAIN;
  const segments = baseUrl.split('/');
  if(range == 'none'){
    DOMAIN = segments.slice(0, 3).join('/');
    window.serverAddress = DOMAIN;
    window.webSocketAddress = DOMAIN.replace('https', 'wss');
  }else if(range == 'front'){
    DOMAIN = segments.slice(0, 4).join('/');
  }else if(range == 'back'){
    DOMAIN = segments.slice(0, segments.length - 1).join('/'); 
  }else if(range == 'fileName'){
    DOMAIN = segments[segments.length - 1];
  }else if(range == 'AAListPath'){
    DOMAIN = segments.slice(4, segments.length - 1).join('/');
  }
  else if(range == 'AListPath'){
    DOMAIN = segments.slice(4, 6).join('/');
  }
  else if(range == 'url'){
    DOMAIN = url;
  }
  return DOMAIN;
}
getDomain();