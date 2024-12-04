<script setup lang="ts"></script>

<template>
	<div class="cell-wrapper">
		<div class="cell"><slot></slot></div>
	</div>
</template>

<style scoped lang="scss">
.cell-wrapper {
	display: flex;
	flex-direction: column;
	align-items: flex-start;

	max-height: 100%;
	height: 100%;
	min-height: 100%;
	width: max-content;
	max-width: 200px;

	overflow: hidden;

	.cell {
		margin: auto 0;
	}
}
</style>
