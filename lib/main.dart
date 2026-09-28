import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

import 'components/control_widget.dart';
import 'domain/bloc/scanner/scanner_bloc.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Code Scanner',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(
          seedColor: const Color(0xFF1F5B3A),
        ),
        scaffoldBackgroundColor: Colors.white,
        appBarTheme: const AppBarTheme(
          backgroundColor: Color(0xFF1F5B3A),
          foregroundColor: Colors.white,
          elevation: 0,
        ),
      ),
      home: BlocProvider(
        create: (_) => ScannerBloc(),
        child: const ControlWidget(),
      ),
    );
  }
}