package com.example.demo.controller;

import java.util.List;

import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.domain.Sort;
import org.springframework.data.web.PageableDefault;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.CrossOrigin;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PatchMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import com.example.demo.dto.CandidateRequestDto;
import com.example.demo.dto.CandidateResponseDto;
import com.example.demo.service.CandidateService;

import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;

@RestController
@RequestMapping("/api/v1/candidates")
@RequiredArgsConstructor
@CrossOrigin(origins = "*")
public class CandidateController {

	private final CandidateService candidateService;

	@PostMapping
	public ResponseEntity<CandidateResponseDto> createCandidate(@Valid @RequestBody CandidateRequestDto candidateDto) {
		CandidateResponseDto createdCandidate = candidateService.createCandidate(candidateDto);
		return new ResponseEntity<>(createdCandidate, HttpStatus.CREATED);
	}

	@GetMapping("/{id}")
	public ResponseEntity<CandidateResponseDto> getCandidateById(@PathVariable Long id) {
		CandidateResponseDto candidate = candidateService.getCandidateById(id);
		return ResponseEntity.ok(candidate);
	}

	@GetMapping
	public ResponseEntity<Page<CandidateResponseDto>> getAllCandidates(
			@PageableDefault(size = 20, sort = "createdAt", direction = Sort.Direction.DESC) Pageable pageable) {
		Page<CandidateResponseDto> candidates = candidateService.getAllCandidates(pageable);
		return ResponseEntity.ok(candidates);
	}

	@PutMapping("/{id}")
	public ResponseEntity<CandidateResponseDto> updateCandidate(@PathVariable Long id,
			@Valid @RequestBody CandidateRequestDto candidateDto) {
		CandidateResponseDto updatedCandidate = candidateService.updateCandidate(id, candidateDto);
		return ResponseEntity.ok(updatedCandidate);
	}

	@DeleteMapping("/{id}")
	public ResponseEntity<Void> deleteCandidate(@PathVariable Long id) {
		candidateService.deleteCandidate(id);
		return ResponseEntity.noContent().build();
	}

	@PatchMapping("/{id}/stage")
	public ResponseEntity<CandidateResponseDto> updatePipelineStage(@PathVariable Long id, @RequestParam String stage) {
		CandidateResponseDto updatedCandidate = candidateService.updatePipelineStage(id, stage);
		return ResponseEntity.ok(updatedCandidate);
	}

	@GetMapping("/search")
	public ResponseEntity<List<CandidateResponseDto>> searchByName(@RequestParam String name) {
		List<CandidateResponseDto> candidates = candidateService.searchCandidatesByName(name);
		return ResponseEntity.ok(candidates);
	}

	@GetMapping("/skill")
	public ResponseEntity<Page<CandidateResponseDto>> searchBySkill(@RequestParam String skill,
			@PageableDefault(size = 20) Pageable pageable) {
		Page<CandidateResponseDto> candidates = candidateService.searchCandidatesBySkill(skill, pageable);
		return ResponseEntity.ok(candidates);
	}
}