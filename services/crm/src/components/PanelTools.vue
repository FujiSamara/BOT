<template>
	<div class="tools-wrapper">
		<slot></slot>
	</div>
</template>
<script setup lang="ts"></script>
<style scoped>
.tools-wrapper {
	display: flex;
	align-items: center;
	justify-content: center;
	flex-direction: row;
	gap: 20px;
	padding: 12px 12px 12px 20px;
	background-color: #ffffff;
	border-radius: 2000px;
	white-space: nowrap;
	overflow: hidden;
	flex-shrink: 0;
}
</style>
