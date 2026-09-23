from intelligence.matching import compare_reports
def cluster_reports(reports,**options):
    clusters=[];matches=[]
    for report in reports:
        found=[]
        for i,cluster in enumerate(clusters):
            comparisons=[compare_reports(report,old,**options) for old in cluster];matches.extend(comparisons)
            if any(x.classification in {'related','duplicate'} for x in comparisons):found.append(i)
        if not found:clusters.append([report])
        else:
            clusters[found[0]].append(report)
            for i in reversed(found[1:]):clusters[found[0]].extend(clusters.pop(i))
    return clusters,matches
