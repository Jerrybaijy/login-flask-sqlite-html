// -----------------------------------登录盒子--------------------------------------

// 关闭登录框
function closeLoginBox() {
  var loginBox = document.getElementById('loginBox');
  if (loginBox) {
    loginBox.style.display = 'none';
  } else {
    console.error('找不到登录框元素！');
  }
}

// 关闭注册框
function closeRegisterBox() {
  var registerBox = document.getElementById('registerBox');
  if (registerBox) {
    registerBox.style.display = 'none';  // 隐藏注册框
  } else {
    console.error('找不到注册框元素！');
  }
}

// -----------------------------------音乐--------------------------------------
