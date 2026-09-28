part of 'scanner_bloc.dart';

abstract class ScannerEvent extends Equatable {
  const ScannerEvent();
  @override
  List<Object?> get props => [];
}

class RecognizeImageEvent extends ScannerEvent {
  final XFile image;
  RecognizeImageEvent(this.image);
  @override
  List<Object?> get props => [image.path];
}

class LoadHistoryEvent extends ScannerEvent {}

class DeleteScanEvent extends ScannerEvent {
  final String id;
  DeleteScanEvent(this.id);
  @override
  List<Object?> get props => [id];
}

class ClearHistoryEvent extends ScannerEvent {}

class ResetScannerEvent extends ScannerEvent {}