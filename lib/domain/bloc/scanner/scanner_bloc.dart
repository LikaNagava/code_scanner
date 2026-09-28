import 'dart:convert';

import 'package:equatable/equatable.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:http/http.dart' as http;
import 'package:image_picker/image_picker.dart';

import '../../models/scan_result.dart';
import '../../storage/history_storage.dart';

part 'scanner_event.dart';
part 'scanner_state.dart';

class ScannerBloc extends Bloc<ScannerEvent, ScannerState> {
  static const String baseUrl = 'https://code-scanner.ru';

  final HistoryStorage _storage = HistoryStorage();
  List<ScanResult> _history = [];

  ScannerBloc() : super(ScannerInitialState()) {
    on<RecognizeImageEvent>(_onRecognize);
    on<LoadHistoryEvent>(_onLoadHistory);
    on<DeleteScanEvent>(_onDelete);
    on<ClearHistoryEvent>(_onClear);
    on<ResetScannerEvent>((event, emit) => emit(ScannerInitialState()));
    add(LoadHistoryEvent());
  }

  Future<void> _onRecognize(
      RecognizeImageEvent event, Emitter<ScannerState> emit) async {
    emit(ScannerLoadingState());
    try {
      final request = http.MultipartRequest(
        'POST',
        Uri.parse('$baseUrl/recognize'),
      );
      final bytes = await event.image.readAsBytes();
      final fileName = event.image.path.split('/').last.split('\\').last;
      request.files.add(
        http.MultipartFile.fromBytes('file', bytes, filename: fileName),
      );
      final streamed = await request
          .send()
          .timeout(const Duration(seconds: 120));
      final response = await http.Response.fromStream(streamed);

      if (response.statusCode != 200) {
        String detail;
        if (response.statusCode == 413) {
          detail = 'Фото слишком большое. Выберите другое.';
        } else if (response.statusCode == 415) {
          detail = 'Такой формат не поддерживается.';
        } else if (response.statusCode == 400) {
          detail = 'Не получилось прочитать фото. Попробуйте другое.';
        } else {
          detail = 'Сервер не смог обработать фото. Попробуйте ещё раз.';
        }
        emit(ScannerErrorState(detail));
        return;
      }

      final data = jsonDecode(response.body) as Map<String, dynamic>;
      final result = ScanResult.fromApi(
        data,
        fileName: event.image.path.split('/').last.split('\\').last,
      );
      _history.insert(0, result);
      await _storage.save(_history);
      emit(ScannerResultState(result, List.unmodifiable(_history)));
    } catch (e) {
      final msg = e.toString();
      String friendly;
      if (msg.contains('SocketException') ||
          msg.contains('Failed host lookup') ||
          msg.contains('ClientException')) {
        friendly = 'Нет соединения с сервером. Проверьте интернет.';
      } else if (msg.contains('TimeoutException')) {
        friendly = 'Сервер не отвечает. Попробуйте ещё раз.';
      } else if (msg.contains('FormatException')) {
        friendly = 'Сервер вернул неожиданный ответ.';
      } else {
        friendly = 'Не удалось распознать. Попробуйте другое фото.';
      }
      emit(ScannerErrorState(friendly));
    }
  }

  Future<void> _onLoadHistory(
      LoadHistoryEvent event, Emitter<ScannerState> emit) async {
    _history = await _storage.load();
    emit(HistoryLoadedState(List.unmodifiable(_history)));
  }

  Future<void> _onDelete(
      DeleteScanEvent event, Emitter<ScannerState> emit) async {
    _history.removeWhere((e) => e.id == event.id);
    await _storage.save(_history);
    emit(HistoryLoadedState(List.unmodifiable(_history)));
  }

  Future<void> _onClear(
      ClearHistoryEvent event, Emitter<ScannerState> emit) async {
    _history = [];
    await _storage.clear();
    emit(HistoryLoadedState(const []));
  }
}