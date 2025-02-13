<script setup lang="ts">
import { PropType } from "vue";
import { DocumentEntity } from "@/components/entity";
import DocumentSelect from "@/components/selects/DocumentSelect.vue";

const props = defineProps({
	entity: {
		type: Object as PropType<DocumentEntity>,
		required: true,
	},
	onlyOne: {
		type: Boolean,
	},
});
const entity = props.entity;
</script>

<template>
	<div class="e-select">
		<span v-if="entity.withTitle" class="title">{{ entity.placeholder }}</span>
		<DocumentSelect
			:documents="entity.selectedEntities.value"
			:only-one="props.onlyOne"
			:placeholder="entity.placeholder"
			:required="entity.required"
			:readonly="entity.readonly"
			@submit="(docs) => entity.submit(docs)"
			@clear="() => entity.clear()"
		></DocumentSelect>
	</div>
</template>

<style scoped lang="scss">
@import "@/components/entity/entity.scss";
</style>
