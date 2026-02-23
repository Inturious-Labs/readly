/**
 * Readly i18n translations
 * Default language: zh (Chinese)
 */
const i18n = {
    zh: {
        // Header
        subtitle: '将任意文章转换为 PDF 和 EPUB',

        // Form
        label_url: '文章链接',
        btn_convert: '转换',

        // About
        about_title: '关于 Readly',
        about_desc: 'Readly 目前处于公测阶段，完全免费使用。它可以将网页文章转换为 PDF 和 EPUB 文件，方便在 reMarkable、文石、汉王、微信读书等设备上离线阅读。粘贴链接，点击转化，然后将文件下载到手机或者电脑。',

        // About subsections
        about_formats_title: '支持的格式和网站',
        about_formats_body: '<p>输出格式：PDF 和 EPUB</p><ul><li>微信公众号文章</li><li>Substack、Medium 等博客平台</li><li>WordPress、Hugo 等静态网站</li><li>大部分公开访问的网页文章</li></ul><p>需要登录或有付费墙的页面可能无法正常转换。</p>',
        about_auth_title: '是否需要登录？',
        about_auth_body: '<p>不需要。Readly 无需注册或登录，打开即用。你的转换记录保存在当前设备上，换一台设备将无法看到之前的记录。</p>',
        about_usecases_title: '使用场景',
        about_usecases_body: '<ul><li>将微信文章保存为 PDF，防止被删除后无法阅读</li><li>把长文转成 EPUB，发送到电子阅读器上舒适阅读</li><li>离线保存感兴趣的文章，方便旅途中阅读</li><li>将网页文章存档备份</li></ul>',
        about_audience_title: '适合谁用？',
        about_audience_body: '<ul><li>在微信公众号上写作的内容创作者，希望永久保存自己文章的副本</li><li>需要保存微信生态中重要文章的研究人员</li><li>喜欢在电子阅读器或纸上阅读长文的读者</li></ul>',

        // Rate limit
        rate_limit_reached: '已达使用上限。',
        resets_in: '重置倒计时',
        resets_within: '将在以内重置',
        conversions_remaining: '次转换剩余',
        of_conversions: '次转换中剩余',
        rate_limit_exceeded: '已达使用上限',
        rate_limit_toast: '已达使用上限，稍后重试',

        // Job list
        no_conversions: '暂无转换记录',
        paste_url: '粘贴链接开始转换',
        last_7_days: '最近 7 天',
        articles: '篇文章',
        article: '篇文章',
        converting: '转换中...',
        starting: '开始中...',
        conversion_failed: '转换失败',
        conversion_complete: '转换完成！',
        connection_failed: '连接失败',
        connection_failed_retry: '连接失败，请重试。',
        show_more: '显示更多',

        // Feedback
        feedback_heading: '每 {window} 分钟可转换 {max} 篇文章',
        feedback_question: '您需要更多吗？',
        feedback_yes: '是的，我需要更多！',
        feedback_no: '不，这些够了',
        feedback_usecase: '您用 Readly 做什么？（可选）',
        feedback_submit: '提交',
        feedback_want_more_thanks: '您告诉我们需要更多——我们正在努力！',
        feedback_thanks: '感谢您的反馈！',

        // Time ago
        just_now: '刚刚',
        m_ago: '分钟前',
        h_ago: '小时前',
        d_ago: '天前',
    },

    en: {
        // Header
        subtitle: 'Convert any article to PDF & EPUB',

        // Form
        label_url: 'Article URL',
        btn_convert: 'Convert',

        // About
        about_title: 'About Readly',
        about_desc: 'Readly is currently in beta and free to use. It converts online articles into PDF and EPUB files, perfect for reading on reMarkable, Boox, Hanvon, WeChat Reader, or any e-reader. Paste a URL, hit convert, then download the files to your phone or computer.',

        // About subsections
        about_formats_title: 'Supported Formats & Sites',
        about_formats_body: '<p>Output formats: PDF and EPUB</p><ul><li>WeChat articles</li><li>Substack, Medium, and other blog platforms</li><li>WordPress, Hugo, and other static sites</li><li>Most publicly accessible web articles</li></ul><p>Pages behind login walls or paywalls may not convert properly.</p>',
        about_auth_title: 'Do I Need to Sign Up?',
        about_auth_body: '<p>No. Readly requires no registration or login — just open and use. Your conversion history is tied to this device, so it won\'t carry over if you switch to a different one.</p>',
        about_usecases_title: 'Use Cases',
        about_usecases_body: '<ul><li>Save WeChat articles as PDF before they get taken down</li><li>Convert long reads to EPUB for comfortable reading on e-readers</li><li>Save articles offline for reading during travel</li><li>Archive and back up web articles</li></ul>',
        about_audience_title: 'Who Is This For?',
        about_audience_body: '<ul><li>Content creators writing on WeChat who want a permanent copy of their own articles</li><li>Researchers who need to preserve important articles from the WeChat ecosystem</li><li>Readers who prefer long-form articles on e-readers or on paper</li></ul>',

        // Rate limit
        rate_limit_reached: 'Rate limit reached.',
        resets_in: 'Resets in',
        resets_within: 'Resets within',
        conversions_remaining: 'conversion(s) remaining',
        of_conversions: 'conversions remaining',
        rate_limit_exceeded: 'Rate limit exceeded',
        rate_limit_toast: 'Rate limit reached — resets soon',

        // Job list
        no_conversions: 'No conversions yet.',
        paste_url: 'Paste a URL above to get started!',
        last_7_days: 'Last 7 Days',
        articles: 'articles',
        article: 'article',
        converting: 'Converting...',
        starting: 'Starting...',
        conversion_failed: 'Conversion failed',
        conversion_complete: 'Conversion complete!',
        connection_failed: 'Connection failed',
        connection_failed_retry: 'Connection failed. Please try again.',
        show_more: 'Show more',

        // Feedback
        feedback_heading: 'You can convert up to {max} articles every {window} minutes',
        feedback_question: 'Would you want more?',
        feedback_yes: 'Yes, I need more!',
        feedback_no: 'No, this is enough',
        feedback_usecase: 'What are you using Readly for? (optional)',
        feedback_submit: 'Submit',
        feedback_want_more_thanks: "You told us you want more — we're working on it!",
        feedback_thanks: 'Thanks for your feedback!',

        // Time ago
        just_now: 'Just now',
        m_ago: 'm ago',
        h_ago: 'h ago',
        d_ago: 'd ago',
    }
};
