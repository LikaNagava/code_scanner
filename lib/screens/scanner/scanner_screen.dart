import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

import '../../domain/bloc/scanner/scanner_bloc.dart';
import '../../domain/localization.dart';

class ScannerScreen extends StatelessWidget {
  final VoidCallback onPickCamera;
  final AppStrings strings;

  const ScannerScreen({
    super.key,
    required this.onPickCamera,
    required this.strings,
  });

  @override
  Widget build(BuildContext context) {
    return BlocBuilder<ScannerBloc, ScannerState>(
      builder: (context, state) {
        final isLoading = state is ScannerLoadingState;
        return Column(
          children: [
            Expanded(
              child: Padding(
                padding: const EdgeInsets.symmetric(horizontal: 20),
                child: GestureDetector(
                  onTap: isLoading ? null : onPickCamera,
                  child: Container(
                    width: double.infinity,
                    decoration: BoxDecoration(
                      border: Border.all(
                        color: const Color(0xFF225B77),
                        width: 2,
                      ),
                      borderRadius: BorderRadius.circular(14),
                    ),
                    child: Center(
                      child: isLoading
                          ? Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          const CircularProgressIndicator(
                            color: Color(0xFF225B77),
                          ),
                          const SizedBox(height: 16),
                          Text(
                            strings.scanning,
                            style: const TextStyle(
                              fontSize: 18,
                              color: Color(0xFF225B77),
                            ),
                          ),
                        ],
                      )
                          : Text(
                        strings.scan,
                        style: const TextStyle(
                          fontSize: 26,
                          fontWeight: FontWeight.bold,
                          color: Color(0xFF225B77),
                          letterSpacing: 2,
                        ),
                      ),
                    ),
                  ),
                ),
              ),
            ),
            const SizedBox(height: 30),
          ],
        );
      },
    );
  }
}