package com.example.demo.service;

import java.util.List;

import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;

import com.example.demo.dto.CandidateRequestDto;
import com.example.demo.dto.CandidateResponseDto;

public interface CandidateService {
	CandidateResponseDto createCandidate(CandidateRequestDto candidateDto);

	CandidateResponseDto updateCandidate(Long id, CandidateRequestDto candidateDto);

	CandidateResponseDto getCandidateById(Long id);

	Page<CandidateResponseDto> getAllCandidates(Pageable pageable);

	void deleteCandidate(Long id);

	CandidateResponseDto updatePipelineStage(Long id, String stage);

	List<CandidateResponseDto> searchCandidatesByName(String name);

	Page<CandidateResponseDto> searchCandidatesBySkill(String skill, Pageable pageable);
}