async function loadScriptAsync(url, ...args) {
  return new Promise((resolve, reject) => {
    var script = document.createElement('script');
    script.type = 'text/javascript';

    script.onload = function() {
      resolve(...args); 
    };

    script.onerror = function() {
      reject(new Error(`Failed to load script: ${url}`));
    };

    script.src = url;
    document.head.appendChild(script);
  });
}

function loadScript(url, callback, ...args) {
    var script = document.createElement('script');
    script.type = 'text/javascript';
  
    script.onload = function() {
      if (callback) {
        callback(...args);
      }
    };
  
    script.src = url;
    document.head.appendChild(script);
  }
  
function loadClassInFunction(url, className, callback, ...args) {
    var script = document.createElement('script');
    script.type = 'text/javascript';
    script.src = url;
  
    // 当脚本加载完成后的回调函数
    script.onload = function() {
      // 通过类名获取加载的类
      const loadedClass = window[className];
  
      if (loadedClass) {
        if (callback) {
          callback(loadedClass, ...args);
        }
      } else {
        console.error(`Failed to load class '${className}' from '${url}'`);
      }
    };
  
    document.head.appendChild(script);
}
  