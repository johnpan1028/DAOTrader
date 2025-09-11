const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();
  
  // 监听控制台日志
  page.on('console', msg => {
    console.log('浏览器控制台:', msg.text());
  });
  
  // 监听网络请求
  page.on('response', response => {
    if (response.url().includes('/api/')) {
      console.log('API响应:', response.url(), response.status());
    }
  });
  
  try {
    // 访问前端页面
    await page.goto('http://localhost:5174');
    
    // 等待页面加载
    await page.waitForTimeout(2000);
    
    // 截图
    await page.screenshot({ path: 'frontend_initial.png', fullPage: true });
    console.log('已保存初始页面截图: frontend_initial.png');
    
    // 填写测试数据
    await page.fill('input[placeholder="如: 000001 或 RB2509"]', 'rb2501');
    await page.selectOption('select', 'futures');
    
    // 点击下载数据按钮
    console.log('点击下载数据按钮...');
    await page.click('button:has-text("下载数据")');
    await page.waitForTimeout(3000);
    
    // 截图
    await page.screenshot({ path: 'frontend_after_download.png', fullPage: true });
    console.log('已保存下载后截图: frontend_after_download.png');
    
    // 点击加载历史数据按钮
    console.log('点击加载历史数据按钮...');
    await page.click('button:has-text("加载历史数据")');
    await page.waitForTimeout(3000);
    
    // 截图
    await page.screenshot({ path: 'frontend_after_load.png', fullPage: true });
    console.log('已保存加载历史数据后截图: frontend_after_load.png');
    
    // 检查K线图是否显示
    const chartContainer = await page.$('.chart-container');
    if (chartContainer) {
        console.log('找到K线图容器');
        const chartRect = await chartContainer.boundingBox();
        console.log('K线图容器尺寸:', chartRect);
        
        // 检查容器内是否有canvas元素（K线图的实际渲染元素）
        const canvasElements = await chartContainer.$$('canvas');
        console.log('找到canvas元素数量:', canvasElements.length);
    } else {
        console.log('未找到K线图容器');
    }
    
    // 检查是否有错误信息
    const errorMessages = await page.$$eval('.message.error', elements => 
      elements.map(el => el.textContent)
    );
    if (errorMessages.length > 0) {
      console.log('错误信息:', errorMessages);
    }
    
    // 检查成功信息
    const successMessages = await page.$$eval('.message.success', elements => 
      elements.map(el => el.textContent)
    );
    if (successMessages.length > 0) {
      console.log('成功信息:', successMessages);
    }
    
    console.log('测试完成，浏览器将保持打开状态供检查...');
    
    // 保持浏览器打开30秒供检查
    await page.waitForTimeout(30000);
    
  } catch (error) {
    console.error('测试过程中出错:', error);
    await page.screenshot({ path: 'frontend_error.png', fullPage: true });
  } finally {
    await browser.close();
  }
})();