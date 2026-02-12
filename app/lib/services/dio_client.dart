import 'package:dio/dio.dart';

import '../config/constants.dart';

class DioClient {
  static final DioClient _instance = DioClient._internal();
  factory DioClient() => _instance;

  late final Dio dio;
  String _language = 'zh-CN';

  DioClient._internal() {
    dio = Dio(BaseOptions(
      baseUrl: AppConfig.apiBaseUrl,
      connectTimeout: const Duration(seconds: 30),
      receiveTimeout: const Duration(seconds: 30),
    ));

    dio.interceptors.add(LogInterceptor(
      request: true,
      requestHeader: true,
      requestBody: true,
      responseHeader: true,
      responseBody: true,
      error: true,
    ));

    dio.interceptors.add(InterceptorsWrapper(
      onRequest: (options, handler) {
        if (options.method == 'GET') {
          options.queryParameters['language'] = _language;
        } else {
          if (options.data is Map<String, dynamic>) {
            (options.data as Map<String, dynamic>)['language'] ??= _language;
          } else if (options.data == null) {
            options.data = {'language': _language};
          }
        }
        handler.next(options);
      },
      onResponse: (response, handler) {
        final body = response.data;
        if (body is Map<String, dynamic> && body.containsKey('code')) {
          if (body['code'] != 0) {
            handler.reject(DioException(
              requestOptions: response.requestOptions,
              message: body['message'] ?? 'Request failed',
            ));
            return;
          }
          response.data = body['data'];
        }
        handler.next(response);
      },
    ));
  }

  void setLanguage(String lang) => _language = lang;
}
