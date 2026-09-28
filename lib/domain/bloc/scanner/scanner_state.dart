part of 'scanner_bloc.dart';

abstract class ScannerState extends Equatable {
  const ScannerState();
  @override
  List<Object?> get props => [];
}

class ScannerInitialState extends ScannerState {}

class ScannerLoadingState extends ScannerState {}

class ScannerResultState extends ScannerState {
  final ScanResult result;
  final List<ScanResult> history;
  ScannerResultState(this.result, this.history);
  @override
  List<Object?> get props => [result, history];
}

class HistoryLoadedState extends ScannerState {
  final List<ScanResult> history;
  HistoryLoadedState(this.history);
  @override
  List<Object?> get props => [history];
}

class ScannerErrorState extends ScannerState {
  final String message;
  ScannerErrorState(this.message);
  @override
  List<Object?> get props => [message];
}
