<script setup lang="ts"></script>

<template>
	<button class="export-button">
		<div class="tool-icon-wrapper">
			<img src="@/assets/icons/excel.svg" />
		</div>
		<span>Выгрузить в Excel</span>
	</button>
</template>

<style scoped lang="scss">
.export-button {
	@include tool;

	span {
		color: $fuji-green;
	}

	border-color: $fuji-green;

	.tool-icon-wrapper {
		.tool-icon {
			width: 24px;
			height: 22px;
		}
	}

	&:hover,
	&.active {
		.tool-icon-wrapper {
			.tool-icon {
				&.search {
					color: $fuji-blue;
				}
			}
		}
	}
}
</style>
