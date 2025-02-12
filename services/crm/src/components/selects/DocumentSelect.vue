<script setup lang="ts">
import { PropType } from "vue";
import { DocumentEntity } from "@/components/entity";

const props = defineProps({
	entity: {
		type: Object as PropType<DocumentEntity>,
		required: true,
	},
});
const entity = props.entity;
</script>

<template>
	<div class="e-select">
		<span v-if="entity.withTitle" class="title">{{ entity.placeholder }}</span>
	</div>
</template>

<style scoped lang="scss">
.ds-wrapper {
	@include field;

	height: 48px;
}
</style>
