import locale


class I18n:

    langs = ("zh_CN", "en_US")

    texts = {
        "ErrSolutionRequestId"                   : (
            "使用请求ID '{request_id}' 前往 https://open-dev.dingtalk.com/fe/api-tools?hash=%23%2Ftroubleshoot 查看解决方案。",
            "Please go to https://open-dev.dingtalk.com/fe/api-tools?hash=%23%2Ftroubleshoot to view the solution using request ID '{request_id}'.",
        ),
        "ErrSolutionCode"                        : (
            "使用错误码 '{code}' 前往 https://open-dev.dingtalk.com/fe/api-tools?hash=%23%2Ftroubleshoot 查看解决方案。",
            "Please go to https://open-dev.dingtalk.com/fe/api-tools?hash=%23%2Ftroubleshoot to view the solution using error code '{code}'.",
        ),
        "ErrSolutionText"                        : (
            "解决方案",
            "Solution",
        ),
        "ErrDefaultMsg"                          : (
            "请求钉钉API时发生错误，服务器返回：{data}",
            "An error occurred while requesting the DingTalk API, the server returned: {data}",
        ),
        "WrongParameterErrorSolution"            : (
            "检查参数是否符合规格。具体请参考当前接口的文档的参数说明和参数示例。",
            "Check if the parameters meet the specifications. For more information, please refer to the parameter description and parameter example of the current interface.",
        ),
        "InvalidParameterErrorSolution"          : (
            "检查下有没有传请求参数，一般发生在http post形式的接口里，没有传参数。",
            "Check if there are request parameters. This error usually occurs in interfaces that use http post, and the parameters are not passed.",
        ),
        "InvalidFileTypeErrorSolution"           : (
            "如果是文件类型，检查下是否是支持。目前只支持doc、docx、xls、xlsx、ppt、pptx、zip、pdf、rar。",
            "If it is a file type, check if it is supported. Currently, only doc, docx, xls, xlsx, ppt, pptx, zip, pdf, and rar are supported.",
        ),
        "InvalidUserIdErrorSolution"             : (
            "请检查userId是否正确，可通过获取部门用户userId列表接口(Dingtalk.get_dept_users)获取。",
            "Please check if the userId is correct. You can get the userId list of department users through the department user list interface (Dingtalk.get_dept_users).",
        ),
        "DepartmentNotExistErrorSolution"        : (
            "可通过获取部门列表接口 (Dingtalk.get_depts) 获取。",
            "You can get the department list through the department list interface (Dingtalk.get_depts).",
        ),
        "ApiPermissionDeniedErrorSolution"       : (
            "需要修改应用对应的权限点。请上开放平台 > 应用详情页 > 权限管理 > 添加接口权限 > 接口权限勾选对应的权限点。",
            "You need to modify the permission points of the corresponding application. Please go to the Open Platform > Application Details page > Permission Management > Add Interface Permission > Check the corresponding permission points.",
        ),
        "IPNotInWhitelistErrorSolution"          : (
            "企业应用：检查配置的服务器出口IP地址是否和请求IP地址一致; ISV应用：检查套件IP白名单和请求IP是否一致。",
            "Enterprise application: Check if the configured server exit IP address is the same as the request IP address; ISV application: Check if the package IP whitelist and the request IP are consistent.",
        ),
        "UserNotFoundErrorSolution"              : (
            "检查该企业下该员工是否存在。",
            "Check if the employee exists in the enterprise.",
        ),
        "APIRateLimitedErrorSolution"            : (
            "当前接口调用超过最高频率限制，触发全局限流，请稍后重试。",
            "The current interface call exceeds the highest frequency limit, triggering global throttling, please try again later.",
        ),
        "NSFWMessageErrorSolution"               : (
            "检测到NSFW内容，请检查并移除相关内容",
            "Please check and remove the NSFW content.",
        ),
        "WebhookUrlExpiredWarning"               : (
            "群组的Webhook链接已经过期！请检查来源IP是否合法、本地时钟是否正确或取消使用缓存。本次将使用API发送",
            "The webhook link for the group has expired! Please check if the source IP is legal, the local clock is correct, or cancel the use of cache. The message will be sent through the API.",
        ),
        "SpecificTemporaryWebhookUrlExpiredError": (
            "指定的临时Webhook链接已经过期",
            "The specified temporary webhook link has expired",
        ),
        "InvalidMessageSendingUrlError"          : (
            "无效的消息发送链接 '{url}'",
            "Invalid message sending link '{url}'",
        ),
        "SendMessageFailedText"                  : (
            "消息发送失败",
            "Message sending failed",
        ),
        "SayaLoadingModuleText"                  : (
            "正在载入模块 {module_name}",
            "Loading module {module_name}",
        ),
        "SayaLoadedModuleText"                   : (
            "模块 {module_name} 载入完成",
            "Module {module_name} loaded successfully",
        ),
        "SayaModuleNotLoadedText"                : (
            "模块 {module_name} 未载入",
            "Module {module_name} not loaded",
        ),
        "DingraiaPreparingLoadingText"           : (
            "正在准备载入",
            "Preparing loading...",
        ),
        "DingraiaLoadCompleteText"               : (
            "载入完成",
            "Load complete",
        ),
        "DingraiaListeningPortText"              : (
            "HTTP服务正在本地端口 {port} 上运行",
            "HTTP service is running on local port {port}",
        ),
        "CtrlCToExitText"                        : (
            "Ctrl-C 已触发",
            "Ctrl-C triggered",
        ),
        "UserForceToExitText"                    : (
            "用户已强制退出",
            "User forced to exit",
        ),
        "StoppingDingraiaText"                   : (
            "正在停止Dingraia...",
            "Stopping Dingraia...",
        ),
        "CancellingAsyncTasksText"               : (
            "正在取消以下的异步任务: [{names}]",
            "Cancelling the following async task: [{names}]",
        ),
        "SingleAsyncTaskCancelledSuccessText"    : (
            "任务 [{name}] 已取消",
            "Task [{name}] cancelled successfully",
        ),
        "SingleAsyncTaskCancelledFailedText"     : (
            "任务 [{name}] 取消失败",
            "Task [{name}] cancelled failed",
        ),
        "AllAsyncTasksCancelledSuccessText"      : (
            "所有异步任务已取消",
            "Async tasks stopped successfully",
        ),
        "DingraiaExitedText"                     : (
            "Dingraia 已退出",
            "Exited.",
        ),
        "LoggerExceptionCatchText"               : (
            "函数 '{record[function]}' 发生了一个错误, 位于进程 '{record[process].name}' ({record[process].id}), "
            "线程 '{record[thread].name}' ({record[thread].id}):",
            "An error has been caught in function '{record[function]}', "
            "process '{record[process].name}' ({record[process].id}), "
            "thread '{record[thread].name}' ({record[thread].id}):"
        ),
        "WaitRadioMessageFinishedText"           : (
            "等待消息处理完成...({timeout}s)",
            "Waiting for message processing finished...({timeout}s)"
        ),
        "RadioMessageRemainText"                 : (
            "等待剩余 {remain} 个消息处理完成...",
            "Waiting for {remain} messages to be processed..."
        ),
        "RadioMessageFinishedText"               : (
            "所有消息已经处理完成",
            "All messages was processed."
        ),
        "WebsocketConnectedText"                 : (
            "[{task_name}] Stream连接已建立",
            "[{task_name}] Websocket connected"
        ),
        "WebsocketClosingText"                   : (
            "[{task_name}] 正在关闭Stream连接...",
            "[{task_name}] Closing the websocket connections..."
        ),
        "WebsocketRetryText"                     : (
            "[{task_name}] 将在 {sec} 秒后重新连接Stream服务",
            "[{task_name}] The stream connection will be reconnected after {sec} seconds"
        ),
        "WebSocketClosedText"                    : (
            "[{task_name}] Stream连接已关闭",
            "[{task_name}] Stream connection was stopped."
        ),
        "NSFWMessageBlockedText"                 : (
            "检测到NSFW内容，系统已自动屏蔽该消息",
            "NSFW content detected, the message has been blocked automatically."
        )
    }

    def __init__(self):
        default_locale = locale.getdefaultlocale()
        self.lang = "zh_CN"
        self.langIndex = 0
        for lang in self.langs:
            if lang == default_locale[0]:
                self.lang = lang
                self.langIndex = self.langs.index(lang)
                break

    def setLang(self, lang: str = None):
        if lang is None:
            self.lang = locale.getdefaultlocale()[0]
            self.langIndex = self.langs.index(self.lang)
            return
        if lang in self.langs:
            self.lang = lang
            self.langIndex = self.langs.index(lang)
        else:
            raise ValueError(f"Unsupported language: {lang}")

    def __getattr__(self, name) -> str:
        text = self.texts.get(name)
        if not isinstance(text, tuple):
            return f"'{name}' was not translated"
        if len(text) < self.langIndex + 1:
            if len(text):
                return text[0]
            return f"'{name}' was not translated"
        return text[self.langIndex]


i18n = I18n()
